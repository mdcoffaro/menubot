"""Import a recipe from a URL. Most recipe sites publish schema.org Recipe data as JSON-LD,
which we pull out of the page and hand to Claude to normalize."""

import json
import re

import httpx
from bs4 import BeautifulSoup

from . import llm
from .models import Ingredient, RecipeIn
from .planner import guess_protein
from .shopping import UNIT_ALIASES

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/126.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml",
}


class ImportError_(RuntimeError):
    pass


def fetch_html(url: str) -> str:
    try:
        resp = httpx.get(url, headers=HEADERS, follow_redirects=True, timeout=20)
        resp.raise_for_status()
    except httpx.HTTPError as e:
        raise ImportError_(f"Couldn't fetch that page ({e}). Paywalled sites may need the paste option.") from e
    return resp.text


def _is_recipe(node: dict) -> bool:
    t = node.get("@type")
    return t == "Recipe" or (isinstance(t, list) and "Recipe" in t)


def find_recipe_jsonld(html: str) -> dict | None:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(tag.string or "")
        except (json.JSONDecodeError, TypeError):
            continue
        stack = [data]
        while stack:
            node = stack.pop()
            if isinstance(node, list):
                stack.extend(node)
            elif isinstance(node, dict):
                if _is_recipe(node):
                    return node
                stack.extend(v for k, v in node.items() if k in ("@graph", "mainEntity", "itemListElement"))
    return None


def page_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "noscript"]):
        tag.decompose()
    return re.sub(r"\n\s*\n+", "\n\n", soup.get_text("\n")).strip()


def import_url(url: str) -> RecipeIn:
    html = fetch_html(url)
    jsonld = find_recipe_jsonld(html)
    if llm.available():
        raw = json.dumps(jsonld, ensure_ascii=False) if jsonld else page_text(html)
        return llm.structure_recipe(raw, source_url=url)
    if not jsonld:
        raise ImportError_("No structured recipe data on that page. Set an API key to let Claude read the page instead.")
    return recipe_from_jsonld(jsonld, url)


# ---------- offline fallback: best-effort parsing without Claude ----------

_UNICODE_FRACTIONS = {"½": ".5", "⅓": ".333", "⅔": ".667", "¼": ".25", "¾": ".75", "⅛": ".125"}
_QTY_RE = re.compile(r"^\s*(\d+\s+\d+/\d+|\d+/\d+|\d*\.?\d+)")


def parse_ingredient(line: str) -> Ingredient:
    text = line.strip()
    for k, v in _UNICODE_FRACTIONS.items():
        text = text.replace(k, v)
    qty = None
    m = _QTY_RE.match(text)
    if m:
        token = m.group(1)
        if " " in token:
            whole, frac = token.split()
            n, d = frac.split("/")
            qty = int(whole) + int(n) / int(d)
        elif "/" in token:
            n, d = token.split("/")
            qty = int(n) / int(d)
        else:
            qty = float(token)
        text = text[m.end():].strip()
    unit = ""
    first, _, rest = text.partition(" ")
    if qty is not None and first.lower().rstrip(".") in UNIT_ALIASES and first:
        unit, text = first.lower().rstrip("."), rest
    item, _, note = text.partition(",")
    return Ingredient(item=item.strip().lower(), qty=qty, unit=unit, aisle="other", staple=False, note=note.strip())


def _minutes(iso: str | None) -> int:
    if not iso:
        return 30
    m = re.match(r"P(?:T)?(?:(\d+)H)?(?:(\d+)M)?", iso)
    if not m or not any(m.groups()):
        return 30
    return int(m.group(1) or 0) * 60 + int(m.group(2) or 0)


def _steps(instructions) -> list[str]:
    if isinstance(instructions, str):
        return [s.strip() for s in instructions.split("\n") if s.strip()]
    steps = []
    for node in instructions or []:
        if isinstance(node, str):
            steps.append(node)
        elif node.get("@type") == "HowToSection":
            steps += _steps(node.get("itemListElement"))
        else:
            steps.append(node.get("text", ""))
    return [s for s in steps if s]


def recipe_from_jsonld(data: dict, url: str) -> RecipeIn:
    yield_ = data.get("recipeYield")
    if isinstance(yield_, list):
        yield_ = yield_[0] if yield_ else None
    servings = int(m.group()) if yield_ and (m := re.search(r"\d+", str(yield_))) else 4
    ingredients = [parse_ingredient(i) for i in data.get("recipeIngredient", [])]
    return RecipeIn(
        title=data.get("name", "Untitled recipe"),
        description=(data.get("description") or "")[:300],
        servings=servings,
        total_minutes=_minutes(data.get("totalTime") or data.get("cookTime")),
        cuisine=(data.get("recipeCuisine") or [""])[0] if isinstance(data.get("recipeCuisine"), list) else data.get("recipeCuisine") or "",
        protein=guess_protein(" ".join(i.item for i in ingredients)),
        tags=["imported"],
        ingredients=ingredients,
        steps=_steps(data.get("recipeInstructions")),
        source_url=url,
    )

"""Turn a set of recipes into one grocery list: scale to servings, merge duplicates, group by aisle."""

import math
from collections import defaultdict
from fractions import Fraction

from .models import AISLE_ORDER, Recipe

UNIT_ALIASES = {
    "teaspoon": "tsp", "teaspoons": "tsp", "tsp": "tsp", "tsps": "tsp", "t": "tsp",
    "tablespoon": "tbsp", "tablespoons": "tbsp", "tbsp": "tbsp", "tbsps": "tbsp", "tbs": "tbsp",
    "cup": "cup", "cups": "cup", "c": "cup",
    "ounce": "oz", "ounces": "oz", "oz": "oz",
    "pound": "lb", "pounds": "lb", "lb": "lb", "lbs": "lb",
    "gram": "g", "grams": "g", "g": "g",
    "kilogram": "kg", "kilograms": "kg", "kg": "kg",
    "milliliter": "ml", "milliliters": "ml", "ml": "ml",
    "liter": "l", "liters": "l", "l": "l",
    "clove": "clove", "cloves": "clove",
    "can": "can", "cans": "can",
    "bunch": "bunch", "bunches": "bunch",
    "pinch": "pinch", "pinches": "pinch",
    "slice": "slice", "slices": "slice",
    "sprig": "sprig", "sprigs": "sprig",
    "head": "head", "heads": "head",
    "package": "package", "packages": "package", "pkg": "package",
    "": "",
}

# Units we can add together, expressed in a base unit.
VOLUME_TSP = {"tsp": 1, "tbsp": 3, "cup": 48, "ml": 0.202884, "l": 202.884}
WEIGHT_OZ = {"oz": 1, "lb": 16, "g": 0.035274, "kg": 35.274}


def normalize_unit(unit: str) -> str:
    u = unit.strip().lower().rstrip(".")
    return UNIT_ALIASES.get(u, u)


def format_qty(q: float) -> str:
    whole = int(q)
    frac = Fraction(q - whole).limit_denominator(4)
    if frac == 1:
        whole, frac = whole + 1, Fraction(0)
    if frac == 0:
        return str(whole)
    return f"{whole} {frac}" if whole else str(frac)


def _volume_str(tsp: float) -> str:
    cups = tsp / 48
    if cups >= 0.25 and abs(float(Fraction(cups).limit_denominator(4)) - cups) / cups < 0.08:
        return f"{format_qty(cups)} cup"
    if tsp >= 3:
        return f"{format_qty(tsp / 3)} tbsp"
    return f"{format_qty(tsp)} tsp"


def _weight_str(oz: float) -> str:
    if oz >= 16:
        return f"{format_qty(oz / 16)} lb"
    return f"{format_qty(oz)} oz"


def _plural(unit: str, qty: float) -> str:
    if qty > 1 and unit in {"clove", "can", "bunch", "slice", "sprig", "head", "package"}:
        return unit + ("es" if unit.endswith("ch") else "s")
    return unit


def build_list(recipes: list[Recipe], servings: int) -> dict:
    # item -> {"volume": tsp, "weight": oz, "other": {unit: qty}, "unquantified": bool, ...}
    totals: dict[str, dict] = {}
    for recipe in recipes:
        scale = servings / recipe.servings if recipe.servings else 1
        for ing in recipe.ingredients:
            key = ing.item.strip().lower()
            entry = totals.setdefault(key, {
                "item": key, "aisle": ing.aisle, "staple": ing.staple,
                "volume": 0.0, "weight": 0.0, "other": defaultdict(float),
                "unquantified": False, "recipes": [],
            })
            entry["staple"] = entry["staple"] and ing.staple
            if recipe.title not in entry["recipes"]:
                entry["recipes"].append(recipe.title)
            if ing.qty is None:
                entry["unquantified"] = True
                continue
            unit = normalize_unit(ing.unit)
            qty = ing.qty * scale
            if unit in VOLUME_TSP:
                entry["volume"] += qty * VOLUME_TSP[unit]
            elif unit in WEIGHT_OZ:
                entry["weight"] += qty * WEIGHT_OZ[unit]
            else:
                entry["other"][unit] += qty

    aisles: dict[str, list] = defaultdict(list)
    staples = []
    for entry in sorted(totals.values(), key=lambda e: e["item"]):
        parts = []
        for unit, qty in entry["other"].items():
            if unit in ("", "clove", "can", "head", "bunch", "package"):
                qty = math.ceil(qty - 1e-9)  # you can't buy 1.5 onions
            parts.append(f"{format_qty(qty)} {_plural(unit, qty)}".strip())
        if entry["weight"]:
            parts.append(_weight_str(entry["weight"]))
        if entry["volume"]:
            parts.append(_volume_str(entry["volume"]))
        line = {"item": entry["item"], "amount": " + ".join(parts) or "as needed", "recipes": entry["recipes"]}
        (staples if entry["staple"] else aisles[entry["aisle"]]).append(line)

    return {
        "aisles": [{"aisle": a, "items": aisles[a]} for a in AISLE_ORDER if aisles.get(a)],
        "staples": staples,
    }


def as_text(shopping: dict) -> str:
    lines = []
    for group in shopping["aisles"]:
        lines.append(group["aisle"].upper())
        lines += [f"- {i['item']} ({i['amount']})" for i in group["items"]]
        lines.append("")
    if shopping["staples"]:
        lines.append("CHECK THE PANTRY")
        lines += [f"- {i['item']}" for i in shopping["staples"]]
    return "\n".join(lines).strip()

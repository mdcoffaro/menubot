"""Everything that talks to Claude: picking meals, inventing a recipe on request, and
turning messy imported recipe text into our structured format."""

import os
from functools import lru_cache

import anthropic
from pydantic import BaseModel, Field, ValidationError

from .models import Recipe, RecipeIn

MODEL = os.environ.get("MENUBOT_MODEL", "claude-opus-5-5")
# Meal picking is a light task; "low" keeps responses snappy. Raise it if picks feel off.
EFFORT = os.environ.get("MENUBOT_EFFORT", "low")
# On a safety-classifier decline, let the API retry on Anthropic's recommended fallback model.
FALLBACK_BETA = "server-side-fallback-2026-07-01"


class LLMError(RuntimeError):
    pass


def available() -> bool:
    if os.environ.get("MENUBOT_OFFLINE"):
        return False
    return any(os.environ.get(k) for k in ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_PROFILE"))


@lru_cache(maxsize=1)
def _client() -> anthropic.Anthropic:
    return anthropic.Anthropic()


def _parse(system: str, user: str, schema: type[BaseModel], max_tokens: int = 16000):
    try:
        response = _client().beta.messages.parse(
            model=MODEL,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
            output_format=schema,
            output_config={"effort": EFFORT},
            betas=[FALLBACK_BETA],
            fallbacks="default",
        )
    except anthropic.AuthenticationError as e:
        raise LLMError("Claude rejected the API key. Check ANTHROPIC_API_KEY.") from e
    except anthropic.RateLimitError as e:
        raise LLMError("Hit the Claude rate limit. Try again in a minute.") from e
    except anthropic.APIStatusError as e:
        raise LLMError(f"Claude API error ({e.status_code}): {e.message}") from e
    except anthropic.APIConnectionError as e:
        raise LLMError("Couldn't reach the Claude API.") from e
    except ValidationError as e:
        raise LLMError("Claude's response didn't match the expected format. Try again.") from e

    if response.stop_reason == "refusal":
        raise LLMError("Claude declined this request. Try rephrasing it.")
    if response.stop_reason == "max_tokens" or response.parsed_output is None:
        raise LLMError("Claude's response was cut off. Try again.")
    return response.parsed_output


# ---------- meal planning ----------

class PlannedMeal(BaseModel):
    day: str
    recipe_id: int = Field(description="ID from the catalog, or 0 when proposing a dish that isn't in the catalog")
    new_dish: str = Field(description="Only when recipe_id is 0: a short description of the dish to create, e.g. 'teriyaki salmon with rice'. Otherwise empty.")
    reason: str = Field(description="One short, friendly sentence on why this pick fits")


class MealPlan(BaseModel):
    meals: list[PlannedMeal]


PLANNER_SYSTEM = """You plan weeknight dinners for a household from their recipe catalog.

How to pick:
- Follow the household's request exactly. Dietary restrictions and dislikes are hard rules; \
"X is ok for one meal" means at most one meal with X.
- If they name a specific dish for a specific day, use the matching catalog recipe; if nothing \
in the catalog matches, set recipe_id to 0 and describe the dish in new_dish.
- Otherwise only pick from the catalog, and only use recipe_id 0 when the catalog truly has \
nothing that fits the request.
- Make the week varied: different cuisines, proteins, and cooking styles. Never repeat a recipe.
- Favor quicker recipes unless they ask otherwise.
- Avoid recipes listed as recently cooked unless they ask for one.
- Return exactly one meal per requested day, using the day names as given."""


def _catalog_line(r: Recipe) -> str:
    main = ", ".join(i.item for i in r.ingredients if not i.staple)[:160]
    tags = ", ".join(r.tags)
    return f"{r.id} | {r.title} | {r.protein} | {r.cuisine} | {r.total_minutes} min | {tags} | {main}"


def plan_meals(
    days: list[str],
    request: str,
    catalog: list[Recipe],
    recently_cooked: list[int] = (),
    keep: dict[str, Recipe] | None = None,
    exclude_ids: list[int] = (),
) -> list[PlannedMeal]:
    """Pick a meal for each day. `keep` holds meals already settled for other days (used when
    swapping one day) so Claude can keep the week balanced around them."""
    excluded = set(exclude_ids)
    lines = [_catalog_line(r) for r in catalog if r.id not in excluded]
    parts = [
        f"Days to plan: {', '.join(days)}",
        f"Household request: {request.strip() or '(no special requests)'}",
    ]
    if keep:
        settled = "; ".join(f"{d}: {r.title} ({r.protein}, {r.cuisine})" for d, r in keep.items())
        parts.append(f"Already planned for the rest of the week (don't repeat these): {settled}")
    if recently_cooked:
        parts.append(f"Recently cooked recipe IDs: {', '.join(map(str, recently_cooked))}")
    parts.append("Catalog (id | title | protein | cuisine | time | tags | key ingredients):\n" + "\n".join(lines))

    plan = _parse(PLANNER_SYSTEM, "\n\n".join(parts), MealPlan)

    valid_ids = {r.id for r in catalog} - excluded
    by_day = {m.day.lower(): m for m in plan.meals}
    result = []
    for day in days:
        meal = by_day.get(day.lower())
        if meal is None:
            raise LLMError(f"Claude didn't return a meal for {day}. Try again.")
        if meal.recipe_id != 0 and meal.recipe_id not in valid_ids:
            raise LLMError(f"Claude picked an unknown recipe for {day}. Try again.")
        meal.day = day
        result.append(meal)
    return result


# ---------- recipe creation ----------

RECIPE_RULES = """Ingredient rules:
- item: the name you'd write on a shopping list, singular and lowercase, without prep words \
("yellow onion", not "1 onion, diced"). Put prep in note.
- Use the same item name for the same thing across recipes ("garlic", "olive oil", "lemon").
- qty is a number (0.5 not "1/2"); use null only for "to taste".
- staple is true only for pantry basics most kitchens already have: salt, black pepper, cooking \
oils, butter, flour, sugar, common dried spices, soy sauce, vinegar.
- protein is the main protein; use "vegetarian" for meatless dishes with dairy/eggs and "vegan" \
for fully plant-based.
- tags: 2 to 5 short lowercase tags, such as weeknight, one-pot, sheet-pan, pasta, spicy, \
make-ahead, grill.
- steps: clear, concise instructions, one action per step."""


def generate_recipe(dish: str, request: str = "", servings: int = 2) -> RecipeIn:
    system = "You are a home-cooking recipe developer. Write a reliable weeknight recipe.\n\n" + RECIPE_RULES
    user = f"Dish: {dish}\nServings: {servings}"
    if request:
        user += f"\nHousehold preferences to respect: {request}"
    return _parse(system, user, RecipeIn)


def structure_recipe(raw: str, source_url: str = "") -> RecipeIn:
    """Convert scraped JSON-LD or pasted recipe text into a RecipeIn."""
    system = (
        "Convert the recipe below into the structured format. Keep the author's quantities and "
        "steps; tidy the wording but don't invent ingredients. If it's not a recipe, return "
        "title 'NOT A RECIPE' with empty ingredients.\n\n" + RECIPE_RULES
    )
    recipe = _parse(system, raw[:60000], RecipeIn)
    if recipe.title.strip().upper() == "NOT A RECIPE" or not recipe.ingredients:
        raise LLMError("That doesn't look like a recipe.")
    recipe.source_url = source_url
    return recipe

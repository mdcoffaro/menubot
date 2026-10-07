"""Plan orchestration: ask Claude (or the offline fallback) for meals, create any new recipes,
and persist the plan."""

import random
import re

from . import db, llm
from .models import Recipe

PROTEIN_WORDS = {
    "chicken": "chicken", "turkey": "turkey", "beef": "beef", "steak": "beef", "pork": "pork",
    "bacon": "pork", "sausage": "pork", "lamb": "lamb", "fish": "fish", "salmon": "fish",
    "cod": "fish", "tuna": "fish", "halibut": "fish", "shrimp": "shellfish", "prawn": "shellfish",
    "scallop": "shellfish", "seafood": "shellfish", "meat": None,
}
MEATS = {"chicken", "turkey", "beef", "pork", "lamb"}
NEGATIVE = re.compile(r"\b(no|not|avoid|without|hate|don'?t|icked|sick of|tired of|skip)\b")
PERMISSIVE = re.compile(r"\b(ok|okay|fine|allowed|can have)\b")


def guess_protein(text: str) -> str:
    text = text.lower()
    for word, protein in PROTEIN_WORDS.items():
        if protein and re.search(rf"\b{word}", text):
            return protein
    return "vegetarian"


def _offline_rules(request: str) -> tuple[set[str] | None, set[str], set[str]]:
    """Very rough reading of the request: (allowed proteins or None for any, banned, allowed once)."""
    text = request.lower()
    allowed = None
    if "vegan" in text:
        allowed = {"vegan"}
    elif re.search(r"vegetarian|veggie|meatless|plant", text):
        allowed = {"vegetarian", "vegan"}
    banned, once = set(), set()
    for sentence in re.split(r"[.,;!?\n]|\b(?:but|and|so)\b", text):
        mentioned = {p for w, p in PROTEIN_WORDS.items() if re.search(rf"\b{w}", sentence)}
        if "meat" in sentence and None in mentioned:
            mentioned |= MEATS
        mentioned.discard(None)
        if PERMISSIVE.search(sentence):
            once |= mentioned
        elif NEGATIVE.search(sentence):
            banned |= mentioned
    return allowed, banned - once, once


def offline_pick(days, request, catalog, recently_cooked=(), keep=None, exclude_ids=()):
    allowed, banned, once = _offline_rules(request)
    used_once = {r.protein for r in (keep or {}).values() if r.protein in once}
    taken = {r.id for r in (keep or {}).values()} | set(exclude_ids)
    picks = []
    for day in days:
        def ok(r: Recipe) -> bool:
            if r.id in taken or r.protein in banned:
                return False
            if r.protein in once:
                return r.protein not in used_once
            return allowed is None or r.protein in allowed
        pool = [r for r in catalog if ok(r)]
        fresh = [r for r in pool if r.id not in recently_cooked] or pool
        if not fresh:
            raise llm.LLMError("No recipes in the catalog match that request. Try loosening it or add recipes.")
        choice = random.choice(fresh)
        taken.add(choice.id)
        if choice.protein in once:
            used_once.add(choice.protein)
        picks.append(llm.PlannedMeal(day=day, recipe_id=choice.id, new_dish="",
                                     reason="Random pick (offline mode: add an API key for smarter picks)."))
    return picks


def _resolve(meals: list[llm.PlannedMeal], request: str, servings: int) -> list[dict]:
    """Turn planner output into stored meals, creating recipes for any brand-new dishes."""
    resolved = []
    for m in meals:
        recipe_id = m.recipe_id
        if recipe_id == 0:
            recipe = db.add_recipe(llm.generate_recipe(m.new_dish, request, servings), source="generated")
            recipe_id = recipe.id
        resolved.append({"day": m.day, "recipe_id": recipe_id, "reason": m.reason})
    return resolved


def _pick(**kwargs) -> list[llm.PlannedMeal]:
    return llm.plan_meals(**kwargs) if llm.available() else offline_pick(**kwargs)


def make_plan(days: list[str], request: str, servings: int) -> dict:
    meals = _pick(days=days, request=request, catalog=db.list_recipes(),
                  recently_cooked=db.recent_recipe_ids())
    plan_id = db.create_plan(request, servings, _resolve(meals, request, servings))
    return db.get_plan(plan_id)


def swap_meal(plan_id: int, day: str, feedback: str = "") -> dict:
    plan = db.get_plan(plan_id)
    current = next((m for m in plan["meals"] if m["day"] == day), None)
    if current is None:
        raise KeyError(day)
    keep = {m["day"]: m["recipe"] for m in plan["meals"] if m["day"] != day}
    request = plan["prompt"]
    if feedback:
        request += f"\nFor this {day} swap specifically: {feedback}"
    exclude = current["rejected_ids"] + [current["recipe"].id] + [r.id for r in keep.values()]
    meals = _pick(days=[day], request=request, catalog=db.list_recipes(),
                  recently_cooked=db.recent_recipe_ids(), keep=keep, exclude_ids=exclude)
    new = _resolve(meals, request, plan["servings"])[0]
    db.replace_meal(plan_id, day, new["recipe_id"], new["reason"])
    return db.get_plan(plan_id)

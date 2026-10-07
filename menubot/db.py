"""SQLite storage. Recipes keep ingredients/steps/tags as JSON columns; plans keep one row per meal."""

import json
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

from .models import Recipe, RecipeIn

DB_PATH = os.environ.get("MENUBOT_DB", str(Path(__file__).resolve().parent.parent / "menubot.db"))

SCHEMA = """
CREATE TABLE IF NOT EXISTS recipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    servings INTEGER NOT NULL DEFAULT 4,
    total_minutes INTEGER NOT NULL DEFAULT 30,
    cuisine TEXT NOT NULL DEFAULT '',
    protein TEXT NOT NULL,
    tags TEXT NOT NULL DEFAULT '[]',
    ingredients TEXT NOT NULL,
    steps TEXT NOT NULL,
    source TEXT NOT NULL DEFAULT 'seed',
    source_url TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prompt TEXT NOT NULL DEFAULT '',
    servings INTEGER NOT NULL DEFAULT 2,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS plan_meals (
    plan_id INTEGER NOT NULL REFERENCES plans(id) ON DELETE CASCADE,
    day TEXT NOT NULL,
    position INTEGER NOT NULL,
    recipe_id INTEGER NOT NULL REFERENCES recipes(id),
    reason TEXT NOT NULL DEFAULT '',
    approved INTEGER NOT NULL DEFAULT 0,
    rejected_ids TEXT NOT NULL DEFAULT '[]',
    PRIMARY KEY (plan_id, day)
);
"""


@contextmanager
def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with connect() as conn:
        conn.executescript(SCHEMA)
        (count,) = conn.execute("SELECT COUNT(*) FROM recipes").fetchone()
    if count == 0:
        from .seed_data import SEED
        for recipe in SEED:
            add_recipe(recipe, source="seed")


# ---------- recipes ----------

def _row_to_recipe(row: sqlite3.Row) -> Recipe:
    d = dict(row)
    for key in ("tags", "ingredients", "steps"):
        d[key] = json.loads(d[key])
    d.pop("created_at", None)
    return Recipe(**d)


def add_recipe(recipe: RecipeIn, source: str) -> Recipe:
    with connect() as conn:
        cur = conn.execute(
            """INSERT INTO recipes (title, description, servings, total_minutes, cuisine, protein,
                                    tags, ingredients, steps, source, source_url)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                recipe.title, recipe.description, recipe.servings, recipe.total_minutes,
                recipe.cuisine, recipe.protein, json.dumps(recipe.tags),
                json.dumps([i.model_dump() for i in recipe.ingredients]),
                json.dumps(recipe.steps), source, recipe.source_url,
            ),
        )
        new_id = cur.lastrowid
    return get_recipe(new_id)


def get_recipe(recipe_id: int) -> Recipe | None:
    with connect() as conn:
        row = conn.execute("SELECT * FROM recipes WHERE id = ?", (recipe_id,)).fetchone()
    return _row_to_recipe(row) if row else None


def list_recipes() -> list[Recipe]:
    with connect() as conn:
        rows = conn.execute("SELECT * FROM recipes ORDER BY title COLLATE NOCASE").fetchall()
    return [_row_to_recipe(r) for r in rows]


def delete_recipe(recipe_id: int) -> bool:
    with connect() as conn:
        in_use = conn.execute("SELECT 1 FROM plan_meals WHERE recipe_id = ? LIMIT 1", (recipe_id,)).fetchone()
        if in_use:
            raise ValueError("Recipe is part of a saved plan")
        cur = conn.execute("DELETE FROM recipes WHERE id = ?", (recipe_id,))
    return cur.rowcount > 0


# ---------- plans ----------

def create_plan(prompt: str, servings: int, meals: list[dict]) -> int:
    """meals: [{day, recipe_id, reason}] in display order."""
    with connect() as conn:
        plan_id = conn.execute(
            "INSERT INTO plans (prompt, servings) VALUES (?, ?)", (prompt, servings)
        ).lastrowid
        conn.executemany(
            "INSERT INTO plan_meals (plan_id, day, position, recipe_id, reason) VALUES (?, ?, ?, ?, ?)",
            [(plan_id, m["day"], i, m["recipe_id"], m.get("reason", "")) for i, m in enumerate(meals)],
        )
    return plan_id


def get_plan(plan_id: int) -> dict | None:
    with connect() as conn:
        plan = conn.execute("SELECT * FROM plans WHERE id = ?", (plan_id,)).fetchone()
        if not plan:
            return None
        rows = conn.execute(
            "SELECT * FROM plan_meals WHERE plan_id = ? ORDER BY position", (plan_id,)
        ).fetchall()
    meals = []
    for r in rows:
        meals.append({
            "day": r["day"],
            "recipe": get_recipe(r["recipe_id"]),
            "reason": r["reason"],
            "approved": bool(r["approved"]),
            "rejected_ids": json.loads(r["rejected_ids"]),
        })
    return {"id": plan["id"], "prompt": plan["prompt"], "servings": plan["servings"],
            "created_at": plan["created_at"], "meals": meals}


def latest_plan_id() -> int | None:
    with connect() as conn:
        row = conn.execute("SELECT id FROM plans ORDER BY id DESC LIMIT 1").fetchone()
    return row["id"] if row else None


def set_approved(plan_id: int, day: str, approved: bool) -> None:
    with connect() as conn:
        conn.execute(
            "UPDATE plan_meals SET approved = ? WHERE plan_id = ? AND day = ?",
            (int(approved), plan_id, day),
        )


def replace_meal(plan_id: int, day: str, recipe_id: int, reason: str) -> None:
    """Swap in a new recipe, remembering the old one so we don't offer it again."""
    with connect() as conn:
        row = conn.execute(
            "SELECT recipe_id, rejected_ids FROM plan_meals WHERE plan_id = ? AND day = ?", (plan_id, day)
        ).fetchone()
        rejected = json.loads(row["rejected_ids"]) + [row["recipe_id"]]
        conn.execute(
            """UPDATE plan_meals SET recipe_id = ?, reason = ?, approved = 0, rejected_ids = ?
               WHERE plan_id = ? AND day = ?""",
            (recipe_id, reason, json.dumps(rejected), plan_id, day),
        )


def recent_recipe_ids(limit_plans: int = 2) -> list[int]:
    """Recipes used in the last few plans, so the planner can avoid repeats week to week."""
    with connect() as conn:
        rows = conn.execute(
            """SELECT DISTINCT recipe_id FROM plan_meals WHERE plan_id IN
               (SELECT id FROM plans ORDER BY id DESC LIMIT ?)""",
            (limit_plans,),
        ).fetchall()
    return [r["recipe_id"] for r in rows]

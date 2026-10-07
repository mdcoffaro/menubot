# Menubot 🍽️

Plan the week's dinners in a couple of minutes. Pick the nights you're cooking and say what you're
in the mood for (e.g. *"no chicken right now, mostly vegetarian, salmon is ok for one meal, teriyaki
salmon on Monday"*). Then approve or swap each meal and take the merged shopping list to the store.

## Quick start

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...      # optional, but this is what makes it smart
.venv/bin/uvicorn menubot.main:app --reload --host 0.0.0.0
```

Open http://localhost:8000. To use it from your phone on the same Wi-Fi, open
`http://<your-laptop-ip>:8000`.

The first run creates `menubot.db` (SQLite) and loads about 40 starter recipes.

## How it works

| Step | What happens |
|---|---|
| **Plan** | Claude reads your request plus a compact list of every recipe in the DB and picks one per night. It treats restrictions as hard rules, keeps the week varied, and avoids recipes from your last two plans. If you ask for a dish that isn't in the DB ("teriyaki salmon Monday"), Claude writes the recipe and saves it. |
| **Approve / swap** | Approve each meal you like. Swap re-picks that night, keeping the rest of the week in mind and never re-offering a recipe you rejected. You can add a note like "something quicker". |
| **Shopping list** | Scales every recipe to your servings, merges duplicates (2 cloves garlic + 3 cloves garlic → 5 cloves; tbsp + cups combine), and groups items by aisle. Pantry staples (salt, oil, spices) go in a separate "check the pantry" section. Checkboxes are saved on the device, and you can copy or share the list as text. |
| **Add recipes** | Paste a recipe link: most recipe sites embed structured schema.org data, which Claude normalizes. For paywalled sites like NYT Cooking, copy the recipe text and use **Paste text**. |

**Without an API key** the app runs in *offline mode*. Picks are random but follow simple rules
("vegetarian", "no chicken", "salmon is ok for one meal"). URL import still works on sites with
structured data.

## Configuration

| Env var | Default | |
|---|---|---|
| `ANTHROPIC_API_KEY` | none | Turns on Claude |
| `MENUBOT_MODEL` | `claude-opus-5-5` | Model used for planning and recipe parsing |
| `MENUBOT_EFFORT` | `low` | Claude effort level: `low` is fast; raise to `medium`/`high` for more careful picks |
| `MENUBOT_DB` | `./menubot.db` | SQLite file path |
| `MENUBOT_OFFLINE` | unset | Set to `1` to force offline mode |

## Project layout

```
menubot/
  main.py        FastAPI routes + serves the UI
  planner.py     plan/swap orchestration and the offline fallback picker
  llm.py         Claude calls (meal picking, recipe generation, recipe normalization)
  shopping.py    scaling, unit merging, aisle grouping
  importer.py    URL fetch + JSON-LD recipe extraction
  db.py          SQLite schema and queries
  models.py      Recipe / Ingredient shapes (shared by DB, API and Claude's structured output)
  seed_data.py   starter recipes, compact format that's easy to edit
  static/        the web UI (plain HTML/CSS/JS, no build step)
tests/
```

Run tests with `.venv/bin/python -m pytest`.

## Ideas for later

- Deploy (Fly.io / Render) so you both use the same plan from your phones
- Ratings after cooking ("would make again"), fed back into the planner
- Pantry tracking so the list skips what you already have
- Instacart / grocery-cart export
- Leftover-aware planning (cook once, eat twice)

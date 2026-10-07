import pytest
from fastapi.testclient import TestClient

from menubot import db, importer, llm, planner, shopping
from menubot.main import app
from menubot.models import Ingredient, Recipe


@pytest.fixture(autouse=True)
def tmp_db(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "test.db"))
    monkeypatch.setenv("MENUBOT_OFFLINE", "1")


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_seed_loads(client):
    assert client.get("/api/status").json()["recipes"] >= 40


def test_offline_plan_respects_request(client):
    prompt = ("My girlfriend is icked out by chicken right now so stick to vegetarian options, "
              "salmon is ok for one meal.")
    for _ in range(10):
        plan = client.post("/api/plans", json={
            "days": ["Friday", "Monday", "Tuesday", "Thursday"], "prompt": prompt, "servings": 2,
        }).json()
        assert [m["day"] for m in plan["meals"]] == ["Monday", "Tuesday", "Thursday", "Friday"]
        proteins = [m["recipe"]["protein"] for m in plan["meals"]]
        assert "chicken" not in proteins
        assert proteins.count("fish") <= 1
        assert set(proteins) <= {"vegetarian", "vegan", "fish"}
        assert len({m["recipe"]["id"] for m in plan["meals"]}) == 4


def test_swap_approve_and_shopping(client):
    plan = client.post("/api/plans", json={"days": ["Monday", "Wednesday"], "prompt": "vegetarian"}).json()
    old = plan["meals"][0]["recipe"]["id"]
    plan = client.post(f"/api/plans/{plan['id']}/meals/Monday/swap", json={"feedback": ""}).json()
    monday = plan["meals"][0]
    assert monday["recipe"]["id"] != old
    assert old in monday["rejected_ids"]
    assert monday["recipe"]["id"] != plan["meals"][1]["recipe"]["id"]

    for day in ("Monday", "Wednesday"):
        plan = client.post(f"/api/plans/{plan['id']}/meals/{day}/approve", json={"approved": True}).json()
    assert all(m["approved"] for m in plan["meals"])

    sl = client.get(f"/api/plans/{plan['id']}/shopping-list").json()
    assert sl["aisles"] and sl["text"]
    assert "salt" not in {i["item"] for g in sl["aisles"] for i in g["items"]}

    assert client.get("/api/plans/latest").json()["id"] == plan["id"]
    assert client.post(f"/api/plans/{plan['id']}/meals/Sunday/swap", json={}).status_code == 404


def test_bad_day_rejected(client):
    assert client.post("/api/plans", json={"days": ["Funday"]}).status_code == 422


def _recipe(id_, servings, ingredients):
    return Recipe(id=id_, title=f"R{id_}", servings=servings, protein="vegetarian",
                  ingredients=ingredients, steps=["cook"])


def test_shopping_merges_and_scales():
    ing = lambda item, qty, unit, aisle="produce", staple=False: Ingredient(
        item=item, qty=qty, unit=unit, aisle=aisle, staple=staple)
    a = _recipe(1, 4, [ing("garlic", 4, "clove"), ing("olive oil", 2, "tbsp", "pantry", True),
                       ing("yellow onion", 1, ""), ing("parmesan", 0.5, "cup", "dairy")])
    b = _recipe(2, 2, [ing("garlic", 2, "cloves"), ing("yellow onion", 0.5, ""),
                       ing("parmesan", 2, "tablespoons", "dairy")])
    result = shopping.build_list([a, b], servings=2)
    items = {i["item"]: i for g in result["aisles"] for i in g["items"]}
    assert items["garlic"]["amount"] == "4 cloves"
    assert items["yellow onion"]["amount"] == "1"  # 0.5 + 0.5
    assert items["parmesan"]["amount"] == "6 tbsp"  # 1/4 cup (scaled from 1/2) + 2 tbsp
    assert [s["item"] for s in result["staples"]] == ["olive oil"]


def test_jsonld_extraction_and_offline_parse():
    html = """<html><head><script type="application/ld+json">
    {"@context": "https://schema.org", "@graph": [{"@type": "WebPage"}, {"@type": ["Recipe"],
      "name": "Teriyaki Salmon", "recipeYield": ["4 servings"], "totalTime": "PT1H5M",
      "recipeIngredient": ["1 1/2 lbs salmon fillets, skin on", "½ cup soy sauce", "2 scallions"],
      "recipeInstructions": [{"@type": "HowToStep", "text": "Mix."}, {"@type": "HowToStep", "text": "Bake."}]}]}
    </script></head></html>"""
    data = importer.find_recipe_jsonld(html)
    r = importer.recipe_from_jsonld(data, "https://example.com/x")
    assert r.title == "Teriyaki Salmon" and r.servings == 4 and r.total_minutes == 65
    assert r.protein == "fish"
    assert (r.ingredients[0].qty, r.ingredients[0].unit, r.ingredients[0].item) == (1.5, "lbs", "salmon fillets")
    assert r.ingredients[1].qty == 0.5 and r.ingredients[2].unit == ""
    assert r.steps == ["Mix.", "Bake."]


def test_offline_rules():
    allowed, banned, once = planner._offline_rules("No meat but shrimp is fine")
    assert allowed is None and "beef" in banned and "shellfish" in once
    allowed, banned, once = planner._offline_rules(
        "icked out by chicken right now so stick to vegetarian options, salmon is ok for one meal")
    assert allowed == {"vegetarian", "vegan"} and banned == {"chicken"} and once == {"fish"}


def test_plan_meals_validates_claude_output(monkeypatch):
    catalog = [_recipe(1, 4, []), _recipe(2, 4, [])]
    monkeypatch.setattr(llm, "_parse", lambda *a, **k: llm.MealPlan(meals=[
        llm.PlannedMeal(day="monday", recipe_id=1, new_dish="", reason="r"),
        llm.PlannedMeal(day="Tuesday", recipe_id=0, new_dish="teriyaki salmon", reason="asked for it"),
    ]))
    meals = llm.plan_meals(["Monday", "Tuesday"], "", catalog)
    assert [m.day for m in meals] == ["Monday", "Tuesday"] and meals[1].new_dish

    monkeypatch.setattr(llm, "_parse", lambda *a, **k: llm.MealPlan(meals=[
        llm.PlannedMeal(day="Monday", recipe_id=99, new_dish="", reason="r")]))
    with pytest.raises(llm.LLMError):
        llm.plan_meals(["Monday"], "", catalog)


def test_delete_and_restore_recipe(client):
    plan = client.post("/api/plans", json={"days": ["Monday"], "prompt": ""}).json()
    used = plan["meals"][0]["recipe"]
    total = len(client.get("/api/recipes").json())

    assert client.delete(f"/api/recipes/{used['id']}").status_code == 200
    ids = {r["id"] for r in client.get("/api/recipes").json()}
    assert used["id"] not in ids and len(ids) == total - 1
    # Old plans still show the deleted recipe and its shopping list.
    assert client.get(f"/api/plans/{plan['id']}").json()["meals"][0]["recipe"]["title"] == used["title"]
    assert client.get(f"/api/plans/{plan['id']}/shopping-list").status_code == 200
    # The planner never picks it again.
    for _ in range(5):
        p = client.post("/api/plans", json={"days": ["Monday", "Tuesday", "Wednesday"]}).json()
        assert used["id"] not in {m["recipe"]["id"] for m in p["meals"]}
    assert client.delete(f"/api/recipes/{used['id']}").status_code == 404

    assert client.post(f"/api/recipes/{used['id']}/restore").status_code == 200
    assert len(client.get("/api/recipes").json()) == total


def test_history_list_and_delete(client):
    first = client.post("/api/plans", json={"days": ["Monday", "Friday"], "prompt": "veggie"}).json()
    second = client.post("/api/plans", json={"days": ["Tuesday"]}).json()
    history = client.get("/api/plans").json()
    assert [p["id"] for p in history] == [second["id"], first["id"]]
    assert history[1]["prompt"] == "veggie"
    assert [m["day"] for m in history[1]["meals"]] == ["Monday", "Friday"]
    assert history[1]["meals"][0]["title"] == first["meals"][0]["recipe"]["title"]

    assert client.delete(f"/api/plans/{second['id']}").status_code == 200
    assert [p["id"] for p in client.get("/api/plans").json()] == [first["id"]]
    assert client.get("/api/plans/latest").json()["id"] == first["id"]
    assert client.delete(f"/api/plans/{second['id']}").status_code == 404


def test_migrates_old_database(tmp_path, monkeypatch):
    import sqlite3
    path = tmp_path / "old.db"
    old_schema = db.SCHEMA.replace("    deleted INTEGER NOT NULL DEFAULT 0,\n", "")
    assert "deleted" not in old_schema
    sqlite3.connect(path).executescript(old_schema)
    monkeypatch.setattr(db, "DB_PATH", str(path))
    db.init_db()
    assert len(db.list_recipes()) >= 40

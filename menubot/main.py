"""HTTP API + static UI. Run with: uvicorn menubot.main:app --reload"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import db, importer, llm, planner, shopping
from .models import RecipeIn

STATIC = Path(__file__).resolve().parent / "static"
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


@asynccontextmanager
async def lifespan(_: FastAPI):
    db.init_db()
    yield


app = FastAPI(title="Menubot", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=STATIC), name="static")


def _llm_errors(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except (llm.LLMError, importer.ImportError_) as e:
        raise HTTPException(502, str(e)) from e


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")


@app.get("/api/status")
def status():
    return {"claude": llm.available(), "model": llm.MODEL if llm.available() else None,
            "recipes": len(db.list_recipes())}


# ---------- plans ----------

class PlanRequest(BaseModel):
    days: list[str] = Field(min_length=1)
    prompt: str = ""
    servings: int = Field(default=2, ge=1, le=12)


class SwapRequest(BaseModel):
    feedback: str = ""


class ApproveRequest(BaseModel):
    approved: bool = True


def _require_plan(plan_id: int) -> dict:
    plan = db.get_plan(plan_id)
    if not plan:
        raise HTTPException(404, "Plan not found")
    return plan


def _check_day(plan: dict, day: str) -> None:
    if day not in {m["day"] for m in plan["meals"]}:
        raise HTTPException(404, f"No meal on {day} in this plan")


@app.post("/api/plans")
def create_plan(req: PlanRequest):
    days = [d for d in DAYS if d in set(req.days)]
    if len(days) != len(set(req.days)):
        raise HTTPException(422, f"Days must be from: {', '.join(DAYS)}")
    return _llm_errors(planner.make_plan, days, req.prompt, req.servings)


@app.get("/api/plans/latest")
def latest_plan():
    plan_id = db.latest_plan_id()
    return db.get_plan(plan_id) if plan_id else None


@app.get("/api/plans/{plan_id}")
def get_plan(plan_id: int):
    return _require_plan(plan_id)


@app.post("/api/plans/{plan_id}/meals/{day}/swap")
def swap(plan_id: int, day: str, req: SwapRequest):
    _check_day(_require_plan(plan_id), day)
    return _llm_errors(planner.swap_meal, plan_id, day, req.feedback)


@app.post("/api/plans/{plan_id}/meals/{day}/approve")
def approve(plan_id: int, day: str, req: ApproveRequest):
    _check_day(_require_plan(plan_id), day)
    db.set_approved(plan_id, day, req.approved)
    return db.get_plan(plan_id)


@app.get("/api/plans/{plan_id}/shopping-list")
def shopping_list(plan_id: int):
    plan = _require_plan(plan_id)
    result = shopping.build_list([m["recipe"] for m in plan["meals"]], plan["servings"])
    result["text"] = shopping.as_text(result)
    return result


# ---------- recipes ----------

class ImportRequest(BaseModel):
    url: str = ""
    text: str = ""


@app.get("/api/recipes")
def recipes():
    return db.list_recipes()


@app.get("/api/recipes/{recipe_id}")
def recipe(recipe_id: int):
    r = db.get_recipe(recipe_id)
    if not r:
        raise HTTPException(404, "Recipe not found")
    return r


@app.post("/api/recipes")
def add_recipe(recipe: RecipeIn):
    return db.add_recipe(recipe, source="manual")


@app.post("/api/recipes/import")
def import_recipe(req: ImportRequest):
    if req.url.strip():
        parsed = _llm_errors(importer.import_url, req.url.strip())
    elif req.text.strip():
        if not llm.available():
            raise HTTPException(400, "Importing pasted text needs a Claude API key.")
        parsed = _llm_errors(llm.structure_recipe, req.text)
    else:
        raise HTTPException(422, "Provide a url or text")
    return db.add_recipe(parsed, source="import")


@app.delete("/api/recipes/{recipe_id}")
def delete_recipe(recipe_id: int):
    try:
        if not db.delete_recipe(recipe_id):
            raise HTTPException(404, "Recipe not found")
    except ValueError as e:
        raise HTTPException(409, str(e)) from e
    return {"ok": True}

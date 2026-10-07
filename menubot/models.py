"""Shared data shapes: what a recipe looks like in the DB, the API, and Claude's output."""

from typing import Literal

from pydantic import BaseModel, Field

Aisle = Literal["produce", "meat", "seafood", "dairy", "bakery", "pantry", "spices", "frozen", "other"]

Protein = Literal[
    "vegetarian", "vegan", "chicken", "turkey", "beef", "pork", "lamb", "fish", "shellfish"
]

AISLE_ORDER: list[str] = ["produce", "meat", "seafood", "dairy", "bakery", "pantry", "spices", "frozen", "other"]


class Ingredient(BaseModel):
    item: str = Field(description="Shopping-list name, singular and lowercase, e.g. 'yellow onion', 'salmon fillet'")
    qty: float | None = Field(description="Numeric amount, or null for 'to taste' / unspecified")
    unit: str = Field(description="Unit like 'cup', 'tbsp', 'lb', 'clove'; empty string for countable items")
    aisle: Aisle
    staple: bool = Field(description="True for things most kitchens already stock: salt, pepper, cooking oils, flour, sugar, common dried spices")
    note: str = Field(default="", description="Prep note, e.g. 'finely chopped'")


class RecipeIn(BaseModel):
    title: str
    description: str = ""
    servings: int = 4
    total_minutes: int = 30
    cuisine: str = ""
    protein: Protein
    tags: list[str] = Field(default_factory=list, description="Short lowercase tags, e.g. 'weeknight', 'one-pot', 'spicy', 'pasta'")
    ingredients: list[Ingredient]
    steps: list[str]
    source_url: str = ""


class Recipe(RecipeIn):
    id: int
    source: str = "seed"  # seed | import | generated

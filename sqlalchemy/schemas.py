"""
schemas.py — Pydantic schemas (request / response validation)
==============================================================
These are NOT database models.  They define the shape of data that comes IN
(request bodies) and goes OUT (response bodies) of the API.

FastAPI uses them to:
  • Validate incoming JSON automatically.
  • Serialise outgoing data to JSON.
  • Generate accurate OpenAPI / Swagger documentation.
"""

from pydantic import BaseModel


class Product(BaseModel):
    id: int
    name: str
    description: str
    price: float
    quantity: int

    # Allows FastAPI to populate this schema directly from a SQLAlchemy ORM
    # object (attribute access) instead of requiring a plain dict.
    model_config = {"from_attributes": True}

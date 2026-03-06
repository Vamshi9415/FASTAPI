# Pydantic schema for Product
# Pydantic's BaseModel validates incoming request data and outgoing response data.
# FastAPI uses these schemas to auto-generate OpenAPI/Swagger docs and enforce
# correct types on all API boundaries.

from pydantic import BaseModel


class Product(BaseModel):
    id: int
    name: str
    description: str
    price: float
    quantity: int

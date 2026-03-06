"""
02 - REST API (GET & POST) — in-memory store
============================================
Demonstrates GET (list all, get by id) and POST using a plain Python list
as the data store.  No database required.

Run:  uvicorn fastapi.rest_api:app --reload
Docs: http://127.0.0.1:8000/docs

Example curl (POST):
    curl -X POST http://127.0.0.1:8000/product \
         -H "Content-Type: application/json" \
         -d '{"id":4,"name":"Titan","description":"Nice watch","price":50,"quantity":3}'

PowerShell (POST):
    Invoke-RestMethod -Method Post -Uri 'http://127.0.0.1:8000/product' \
        -ContentType 'application/json' \
        -Body '{"id":4,"name":"Titan","description":"Nice watch","price":50,"quantity":3}'
"""

from fastapi import FastAPI, HTTPException

from .schemas import Product

app = FastAPI()

# ── In-memory data store ──────────────────────────────────────────────────────
products: list[Product] = [
    Product(id=1, name="Phone",  description="Budget phone",  price=99,  quantity=10),
    Product(id=2, name="Laptop", description="Gaming laptop", price=999, quantity=6),
    Product(id=5, name="Pen",    description="Blue pen",      price=1,   quantity=100),
    Product(id=6, name="Table",  description="Office table",  price=299, quantity=20),
]


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/")
def greet():
    return "Welcome to the server"


@app.get("/products")
def get_all_products():
    # FastAPI (via Starlette) automatically serialises return values to JSON.
    return products


@app.get("/products/{id}", response_model=Product)
# response_model validates & serialises the return value against the Pydantic
# schema, strips extra fields, and powers the Swagger response documentation.
def get_product_by_id(id: int):
    for prod in products:
        if prod.id == id:
            return prod
    raise HTTPException(status_code=404, detail="Product not found")


@app.post("/product")
def add_product(product: Product):
    if any(p.id == product.id for p in products):
        raise HTTPException(
            status_code=400,
            detail=f"Product with id {product.id} already exists",
        )
    products.append(product)
    return product

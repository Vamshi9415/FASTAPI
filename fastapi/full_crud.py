"""
03 - Full CRUD API — in-memory store
=====================================
Extends rest_api.py with PUT (update) and DELETE routes, still backed by a
plain Python list — no database required.

Run:  uvicorn fastapi.full_crud:app --reload
Docs: http://127.0.0.1:8000/docs
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
    return products


@app.get("/products/{id}", response_model=Product)
def get_product_by_id(id: int):
    for prod in products:
        if prod.id == id:
            return prod
    raise HTTPException(status_code=404, detail="Product not found")


@app.post("/product", response_model=Product, status_code=201)
def add_product(product: Product):
    if any(p.id == product.id for p in products):
        raise HTTPException(
            status_code=400,
            detail=f"Product with id {product.id} already exists",
        )
    products.append(product)
    return product


@app.put("/product", response_model=Product)
def update_product(id: int, product: Product):
    for i, prod in enumerate(products):
        if prod.id == id:
            products[i] = product
            return product
    raise HTTPException(status_code=404, detail="Product not found")


@app.delete("/product")
def delete_product(id: int):
    for i, prod in enumerate(products):
        if prod.id == id:
            del products[i]
            return {"message": "Product deleted successfully"}
    raise HTTPException(status_code=404, detail="Product not found")

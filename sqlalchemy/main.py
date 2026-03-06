"""
main.py — FastAPI + SQLAlchemy full CRUD app
=============================================
Connects a FastAPI application to a PostgreSQL database via SQLAlchemy.
All data is persisted — unlike the in-memory examples in fastapi/.

Run:  uvicorn sqlalchemy.main:app --reload
Docs: http://127.0.0.1:8000/docs

Database config is read from environment variables (see database.py).
"""

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import models
from .database import engine, session
from .schemas import Product

app = FastAPI()

# Create all tables defined in models.py (runs once at startup).
models.Base.metadata.create_all(bind=engine)


# ── Seed data ─────────────────────────────────────────────────────────────────
_seed_products = [
    Product(id=1, name="Phone",  description="Budget phone",  price=99,  quantity=10),
    Product(id=2, name="Laptop", description="Gaming laptop", price=999, quantity=6),
    Product(id=5, name="Pen",    description="Blue pen",      price=1,   quantity=100),
    Product(id=6, name="Table",  description="Office table",  price=299, quantity=20),
]


def _seed_db(db: Session) -> None:
    """Insert seed data only when the table is empty."""
    if db.query(models.Product).count() == 0:
        for product in _seed_products:
            db.add(models.Product(**product.model_dump()))
        db.commit()


# Seed once at import time.
with session() as db:
    _seed_db(db)


# ── Dependency ────────────────────────────────────────────────────────────────
def get_db():
    """
    Yield a database session for a single request, then close it.
    FastAPI's Depends() calls this automatically for every route that needs it.
    """
    db = session()
    try:
        yield db
    finally:
        db.close()


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/")
def greet():
    return "Welcome to the server"


@app.get("/products")
def get_all_products(db: Session = Depends(get_db)):
    # Depends(get_db) tells FastAPI to call get_db(), inject the session, and
    # close it automatically after the response is sent.
    return db.query(models.Product).all()


@app.get("/products/{id}", response_model=Product)
def get_product_by_id(id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.post("/product", response_model=Product, status_code=201)
def add_product(product: Product, db: Session = Depends(get_db)):
    if db.query(models.Product).filter(models.Product.id == product.id).first():
        raise HTTPException(
            status_code=400,
            detail=f"Product with id {product.id} already exists",
        )
    db_product = models.Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    # db.refresh() reloads the object from the DB so the response contains any
    # server-generated values (e.g. auto-increment ids, default timestamps).
    db.refresh(db_product)
    return db_product


@app.put("/product", response_model=Product)
def update_product(id: int, product: Product, db: Session = Depends(get_db)):
    db_prod = db.query(models.Product).filter(models.Product.id == id).first()
    if not db_prod:
        raise HTTPException(status_code=404, detail="Product not found")

    for key, value in product.model_dump().items():
        setattr(db_prod, key, value)

    db.commit()
    db.refresh(db_prod)
    return db_prod


@app.delete("/product")
def delete_product(id: int, db: Session = Depends(get_db)):
    db_prod = db.query(models.Product).filter(models.Product.id == id).first()
    if not db_prod:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(db_prod)
    db.commit()
    return {"message": "Product deleted successfully"}

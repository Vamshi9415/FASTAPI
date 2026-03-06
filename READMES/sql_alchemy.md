# FastAPI + SQLAlchemy — Database Session Management Guide

> Complete guide on Do's, Don'ts, Pitfalls, and how Dependency Injection works with database sessions.

---

## Table of Contents

1. [The Problem — What Goes Wrong](#1-the-problem)
2. [Understanding yield](#2-understanding-yield)
3. [The Fix — Depends](#3-the-fix)
4. [Why Depends Doesn't Work in init_db](#4-why-depends-doesnt-work-in-init_db)
5. [Complete Correct Code](#5-complete-correct-code)
6. [Do's and Don'ts](#6-dos-and-donts)
7. [Common Pitfalls](#7-common-pitfalls)
8. [Key Concepts Summary](#8-key-concepts-summary)

---

## 1. The Problem

The most common mistake — opening a DB session in every route and **never closing it**.

```python
# ❌ BAD — repeated in every single route
@app.get("/products")
def get_all_products():
    db = session()          # opens connection
    result = db.query(...)  # do work
    return result           # connection NEVER CLOSED 💀
```

### What actually happens:

1. A new DB connection opens on every request
2. The connection is never closed
3. Connections pile up until the DB pool is exhausted
4. App crashes with **"too many connections"** error

> ⚠️ **Bonus bug:** Routes were reading/writing to an in-memory `products = [...]` list instead of the actual database — so all data changes were lost on every server restart.

---

## 2. Understanding yield

Before understanding the fix, you need to understand `yield`.

### `return` vs `yield`

| | `return` | `yield` |
|---|---|---|
| Exits function | immediately ✅ | just pauses ❌ |
| Can resume | no | yes ✅ |
| Cleanup code after it | never runs | always runs ✅ |
| Creates generator | no | yes ✅ |

```python
# return — cleanup is impossible
def get_db_BAD():
    db = session()
    return db        # function ends here
    db.close()       # NEVER runs ❌

# yield — cleanup is guaranteed
def get_db_GOOD():
    db = session()
    yield db         # pauses here, hands db to caller
    db.close()       # ALWAYS runs after caller finishes ✅
```

### The Baton Pass

`yield db` means:
> *"I'm done setting up. Here's the db. You take over. I'll wait here until you're finished, then I'll clean up."*

```
get_db() called
    ↓
db = session()              ← setup runs
    ↓
yield db  ──gives db──►  your route receives db
    │                        │
(paused, waiting...)         does its work
    │                        │
    ◄──── route finishes ────┘
    ↓
db.close()                  ← cleanup ALWAYS runs ✅
```

### Why yield Creates a Generator

When a function has `yield`, calling it doesn't run the code — it creates a **generator object**. FastAPI internally does roughly this:

```python
gen = get_db()          # nothing runs yet
db  = next(gen)         # runs until yield, gives db
run_your_route(db)      # your route executes
gen.close()             # triggers finally → db.close()
```

---

## 3. The Fix

### Step 1 — Define `get_db()` once

```python
from fastapi import Depends
from sqlalchemy.orm import Session

def get_db():
    db = session()   # open
    try:
        yield db     # hand to route
    finally:
        db.close()   # ALWAYS closes, even if route raised an error
```

Define this **exactly once**. Never copy-paste session logic into routes again.

### Step 2 — Inject into routes with `Depends`

```python
@app.get("/products")
def get_all_products(db: Session = Depends(get_db)):
    return db.query(database_models.Product).all()

@app.get("/products/{id}")
def get_product_by_id(id: int, db: Session = Depends(get_db)):
    product = db.query(database_models.Product)\
               .filter(database_models.Product.id == id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Not found")
    return product
```

### How `Depends` works

`Depends(get_db)` tells FastAPI:
> *"Before running this route, call `get_db()`, inject whatever it yields as `db`, and clean up after the route finishes."*

You **never call `get_db()` yourself** — FastAPI handles it automatically on every request.

---

## 4. Why `Depends` Doesn't Work in `init_db`

`Depends` is a **FastAPI feature** — it only works inside route functions during request handling.

```python
# ❌ IMPOSSIBLE — nobody to inject at startup
def init_db(db: Session = Depends(get_db)):
    ...
```

### The Execution Timeline

```
App starts
    ↓
init_db() runs  ← NO request, NO FastAPI magic
                  must manage db manually here
    ↓
App is ready and listening
    ↓
Request arrives ← NOW FastAPI is active
                  Depends works here ✅
```

### Correct `init_db` Pattern

```python
# ✅ Pass db manually — no Depends
def init_db(db: Session):
    count = db.query(database_models.Product).count()  # note the ()
    if count == 0:
        for product in products:
            db.add(database_models.Product(**product.model_dump()))
        db.commit()

# Call it at startup using a manual session
with session() as db:
    init_db(db)
```

The `with` statement acts like `try/finally` — it opens the session, runs the block, and closes it automatically.

### Simple Rule

| Situation | Use |
|---|---|
| Inside a FastAPI route | `Depends(get_db)` ✅ |
| App startup | manual `with session() as db` ✅ |
| CLI scripts / background tasks | manual `with session() as db` ✅ |

> **`Depends` = FastAPI request time only. Everything else = manual.**

---

## 5. Complete Correct Code

```python
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from database import session, engine
import database_models
from models import Product

app = FastAPI()
database_models.Base.metadata.create_all(bind=engine)

# ✅ Define once — handles open, yield, and close
def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()

products = [
    Product(id=1, name="Phone",  description="Budget phone",  price=99,  quantity=10),
    Product(id=2, name="Laptop", description="Gaming laptop", price=999, quantity=6),
    Product(id=5, name="Pen",    description="Blue pen",      price=1,   quantity=100),
    Product(id=6, name="Table",  description="Office table",  price=299, quantity=20)
]

# ✅ Startup: manual session (Depends not available here)
def init_db(db: Session):
    if db.query(database_models.Product).count() == 0:
        for product in products:
            db.add(database_models.Product(**product.model_dump()))
        db.commit()

with session() as db:
    init_db(db)

# ✅ All routes use Depends — no manual session management
@app.get("/")
def print_greet():
    return "Welcome to server"

@app.get("/products")
def get_all_products(db: Session = Depends(get_db)):
    return db.query(database_models.Product).all()

@app.get("/products/{id}", response_model=Product)
def get_product_by_id(id: int, db: Session = Depends(get_db)):
    product = db.query(database_models.Product)\
               .filter(database_models.Product.id == id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.post("/product")
def add_product(product: Product, db: Session = Depends(get_db)):
    existing = db.query(database_models.Product)\
                 .filter(database_models.Product.id == product.id).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Product with id {product.id} already exists")
    db_product = database_models.Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@app.put("/product", response_model=Product)
def update_product(id: int, product: Product, db: Session = Depends(get_db)):
    db_product = db.query(database_models.Product)\
                   .filter(database_models.Product.id == id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    for key, value in product.model_dump().items():
        setattr(db_product, key, value)
    db.commit()
    db.refresh(db_product)
    return db_product

@app.delete("/product")
def delete_product(id: int, db: Session = Depends(get_db)):
    db_product = db.query(database_models.Product)\
                   .filter(database_models.Product.id == id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(db_product)
    db.commit()
    return "Product Deleted"
```

---

## 6. Do's and Don'ts

### ✅ DO

- Define `get_db()` once with `yield` + `try/finally`
- Use `Depends(get_db)` in every route
- Always query from the **database**, not in-memory lists
- Use `with session() as db` for startup and scripts
- Call `.count()` with parentheses
- Use `db.refresh()` after commit to get the latest data from DB

### ❌ DON'T

- Open `db = session()` manually inside route functions
- Forget to close the session — causes connection leaks
- Use `Depends` outside of FastAPI route functions
- Store live application data in in-memory Python lists
- Write `.count` without `()` — it returns the method, not a number
- Repeat `try/finally` session logic in every single route

---

## 7. Common Pitfalls

### Pitfall 1 — Missing `()` on `.count`

```python
# ❌ Bug — count is a method reference, always truthy
count = db.query(Product).count
if count == 0:  # NEVER triggers
    ...

# ✅ Correct
count = db.query(Product).count()
```

### Pitfall 2 — Reading from In-Memory List Instead of DB

```python
# ❌ Bug — returns stale list, ignores the actual database
@app.get("/products")
def get_all_products():
    return products  # this list never reflects DB changes!

# ✅ Correct
@app.get("/products")
def get_all_products(db: Session = Depends(get_db)):
    return db.query(database_models.Product).all()
```

### Pitfall 3 — f-string Not Used in HTTPException

```python
# ❌ Bug — prints literal text "{product.id}"
raise HTTPException(detail="Product with id {product.id} already exists")

# ✅ Correct — use f-string
raise HTTPException(detail=f"Product with id {product.id} already exists")
```

### Pitfall 4 — Forgetting `db.refresh()` After Commit

```python
# ❌ May return stale or incomplete object (e.g. missing auto-generated id)
db.add(new_product)
db.commit()
return new_product

# ✅ refresh() reloads the object from DB with the latest values
db.add(new_product)
db.commit()
db.refresh(new_product)
return new_product
```

---

## 8. Key Concepts Summary

| Concept | What It Means |
|---|---|
| `yield` | Pauses a function and hands a value to the caller. Code after `yield` runs when the caller is done — perfect for cleanup. |
| Generator | A function with `yield`. Doesn't run immediately — produces values on demand and can be resumed. |
| `Depends(get_db)` | Tells FastAPI to call `get_db()`, inject the result into the route, and handle cleanup automatically. |
| `try / finally` | `finally` block always runs — even if an exception was raised. Used to guarantee `session.close()`. |
| `with session()` | Context manager that opens and closes the session automatically. Used outside routes. |
| `db.refresh()` | Reloads the object from the database after a commit. Ensures you return the latest data. |
| `.count()` | Must include `()`. Without them it returns the method object, not a number. |
| `model_dump()` | Converts a Pydantic model to a dict. `**` unpacks it into keyword arguments for the SQLAlchemy constructor. |
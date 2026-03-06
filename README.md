# FastAPI Complete Guide — Inventory App (Backend)
> Based on the full course by Ain Reddi.  
> Every file below shows the **buggy version first**, the **error message it produces**, then the **fixed version** — so you learn exactly what went wrong and why.

---

## Table of Contents

1. [Prerequisites & Project Structure](#1-prerequisites--project-structure)
2. [Environment Setup](#2-environment-setup)
3. [Your First FastAPI Server — `main.py`](#3-your-first-fastapi-server--mainpy)
4. [In-Memory Models — `models.py`](#4-in-memory-models--modelspy)
5. [In-Memory CRUD — `main.py`](#5-in-memory-crud--mainpy)
6. [Pydantic Models — `models.py`](#6-pydantic-models--modelspy)
7. [Database Config — `database.py`](#7-database-config--databasepy)
8. [ORM Model — `database_models.py`](#8-orm-model--database_modelspy)
9. [Database CRUD — `main.py`](#9-database-crud--mainpy)
10. [CORS & Frontend Connection — `main.py`](#10-cors--frontend-connection--mainpy)
11. [Complete Final Files](#11-complete-final-files)

---

## 1. Prerequisites & Project Structure

**Requirements**

| Tool | Version | Check |
|---|---|---|
| Python | 3.12+ | `python --version` |
| Node.js | 22+ (optional, for React UI) | `node --version` |
| VS Code / PyCharm | Any | — |
| PostgreSQL | 16 or 17 | postgresql.org |
| pgAdmin 4 | Bundled with PostgreSQL | — |

**Folder layout**

```
FASTAPI/
│
├── fastapi/                     ← Pure FastAPI examples (no database)
│   ├── schemas.py               ← Pydantic schema (shared by all examples)
│   ├── hello_world.py           ← 01: basic GET route
│   ├── rest_api.py              ← 02: GET + POST with in-memory list
│   └── full_crud.py             ← 03: full CRUD with in-memory list
│
└── sqlalchemy/                  ← SQLAlchemy + FastAPI (PostgreSQL)
    ├── database.py              ← Engine & session factory
    ├── models.py                ← SQLAlchemy ORM models (DB tables)
    ├── schemas.py               ← Pydantic schemas (request/response)
    └── main.py                  ← Full CRUD API backed by PostgreSQL
```

**How to run each example**

```bash
# 01 — Hello World
uvicorn fastapi.hello_world:app --reload

# 02 — REST API (GET + POST, in-memory)
uvicorn fastapi.rest_api:app --reload

# 03 — Full CRUD (GET + POST + PUT + DELETE, in-memory)
uvicorn fastapi.full_crud:app --reload

# 04 — Full CRUD (PostgreSQL via SQLAlchemy)
uvicorn sqlalchemy.main:app --reload
```

---

## 2. Environment Setup

### Create & activate a virtual environment

```bash
# Create
python -m venv my_environment

# Activate — PowerShell
.\my_environment\Scripts\Activate.ps1

# Activate — Command Prompt
my_environment\Scripts\activate.bat

# Activate — Mac / Linux
source my_environment/bin/activate
```

You know it worked when `(my_environment)` appears before your terminal path.

```bash
deactivate    # to exit the environment
```

### Install packages (always inside the activated environment)

```bash
pip install fastapi uvicorn           # core
pip install sqlalchemy psycopg2       # for PostgreSQL
```

### Run the React frontend (optional)

```bash
cd frontend
npm install     # first time only — downloads node_modules
npm start       # runs on http://localhost:3000
```

---

## 3. Your First FastAPI Server — `main.py`

---

### ❌ Buggy version

```python
# main.py — BROKEN
from fastapi import FastAPI

app = FastAPI()

# BUG 1: function prints to console instead of returning to browser
@app.get("/")
def greet():
    print("Welcome to ListTrack")   # ← print() does nothing for web responses
```

**Error you see in the browser:**
```
null
```
The endpoint responds with no body because `print()` writes to the terminal, not the HTTP response.

**How to run (also broken):**
```bash
uvicorn main          # ← BUG 2: missing the object name after the colon
```

**Error you see in the terminal:**
```
Error loading ASGI app. Import string "main" must be in format "<module>:<attribute>".
```

**Why:** Uvicorn needs to know both the file (`main`) and the FastAPI object name (`app`).  
Also, `FastAPI` was not defined before — if you forget the import you get:
```
NameError: name 'FastAPI' is not defined
```

---

### ✅ Fixed version

```python
# main.py — CORRECT
from fastapi import FastAPI          # ← must import FastAPI from the library

app = FastAPI()                      # ← create the FastAPI instance

@app.get("/")
def greet():
    return "Welcome to ListTrack"   # ← return sends data in the HTTP response
```

**Run correctly:**
```bash
uvicorn main:app --reload
# main  = filename (main.py)
# app   = the FastAPI object
# --reload = auto-restart on file save
```

Visit `http://localhost:8000` → `"Welcome to ListTrack"`  
Visit `http://localhost:8000/docs` → Free Swagger UI

---

## 4. In-Memory Models — `models.py`

---

### ❌ Buggy version

```python
# models.py — BROKEN
class Product:
    # BUG: no __init__ constructor defined
    # You cannot create Product(id=1, name="Phone", ...) — Python won't accept it
    pass
```

**Error when used in main.py:**
```python
products = [Product(id=1, name="Phone", description="Budget phone", price=99, quantity=10)]
# TypeError: Product() takes no arguments
```

---

### ✅ Fixed version

```python
# models.py — CORRECT
class Product:
    def __init__(self, id: int, name: str, description: str, price: float, quantity: int):
        self.id = id
        self.name = name
        self.description = description
        self.price = price
        self.quantity = quantity
```

---

## 5. In-Memory CRUD — `main.py`

All five endpoints together. Each has a buggy version, error, and fix.

---

### GET all products

#### ❌ Buggy version
```python
# main.py — BROKEN
from fastapi import FastAPI
# BUG: missing import for Product model
# from models import Product   ← not imported

app = FastAPI()

products = [
    Product(id=1, name="Phone", description="Budget phone", price=99, quantity=10),
]

@app.get("/products")
def get_all_products():
    return products
```

**Error:**
```
NameError: name 'Product' is not defined
```

#### ✅ Fixed version
```python
from fastapi import FastAPI
from models import Product           # ← import the class

app = FastAPI()

products = [
    Product(id=1, name="Phone",  description="Budget phone",   price=99,  quantity=10),
    Product(id=2, name="Laptop", description="Gaming laptop",  price=999, quantity=6),
    Product(id=5, name="Pen",    description="Blue pen",       price=1,   quantity=100),
    Product(id=6, name="Table",  description="Office table",   price=299, quantity=20),
]

@app.get("/products")
def get_all_products():
    return products
```

---

### GET one product by ID

#### ❌ Buggy version
```python
# main.py — BROKEN
@app.get("/products/{id}")
def get_product(id: int):
    return products[id - 1]    # BUG: assumes IDs are 0-based sequential (1,2,3,4...)
                               # Our IDs are: 1, 2, 5, 6
                               # Requesting id=5 → products[4] → IndexError!
```

**Error:**
```
Internal Server Error
# In the terminal:
IndexError: list index out of range
```

Also, even when IDs happen to exist, the wrong product is returned.  
`id=5` would try `products[4]` which doesn't exist, instead of the Pen with `id=5`.

#### ✅ Fixed version
```python
@app.get("/products/{id}")
def get_product_by_id(id: int):
    for product in products:
        if product.id == id:     # ← match by the .id attribute, not list index
            return product
    return "Product not found"
```

---

### POST — add a product

#### ❌ Buggy version
```python
# main.py — BROKEN
@app.post("/products")
def add_product(product: Product):
    products.append(product)
    # BUG: returns nothing
    # FastAPI will return null/None — the caller has no confirmation
```

**What you see in Swagger:**
```json
null
```

Also — if you try to test this from the browser URL bar:
```
GET http://localhost:8000/products   ← only GET works from a browser address bar
POST cannot be tested this way — use Swagger (/docs) or Postman
```

#### ✅ Fixed version
```python
@app.post("/products")
def add_product(product: Product):
    products.append(product)
    return product               # ← return the added product as confirmation
```

---

### PUT — update a product

#### ❌ Buggy version
```python
# main.py — BROKEN
@app.put("/products/{id}")
def update_product(id: int, product: Product):
    for i in range(len(products)):
        if products[i].id == id:
            products[i] = product
            return "Product updated successfully"
    # BUG: no return statement when product is NOT found
    # FastAPI silently returns null
```

**What you see:**
```json
null
```
No indication of whether the update succeeded or the product didn't exist.

#### ✅ Fixed version
```python
@app.put("/products/{id}")
def update_product(id: int, product: Product):
    for i in range(len(products)):
        if products[i].id == id:
            products[i] = product
            return "Product updated successfully"
    return "Product not found"   # ← always return something
```

---

### DELETE — remove a product

#### ❌ Buggy version
```python
# main.py — BROKEN
@app.delete("/products/{id}")
def delete_product(id: int):
    for product in products:           # BUG: iterating products directly
        if product.id == id:
            products.remove(product)   # ← modifying a list while iterating it
            return "Product deleted"   #   can skip items or behave unexpectedly
    return "Product not found"
```

**What can happen:**  
Python allows this but it's dangerous — when you remove an item during iteration, the loop shifts indices and may silently skip the next element.

#### ✅ Fixed version
```python
@app.delete("/products/{id}")
def delete_product(id: int):
    for i in range(len(products)):     # ← iterate by index, not by item
        if products[i].id == id:
            del products[i]            # ← delete by index position (safe)
            return "Product deleted"
    return "Product not found"
```

---

## 6. Pydantic Models — `models.py`

Pydantic replaces the plain class. It adds automatic type validation and JSON parsing.

---

### ❌ Buggy version

```python
# models.py — BROKEN
from pydantic import BaseModel

class Product(BaseModel):
    id: int
    name: str
    description: str
    price: float
    quantity: int

# Somewhere in main.py:
products = [
    Product(1, "Phone", "Budget phone", 99, 10)   # BUG: positional args not supported
]
```

**Error:**
```
TypeError: Product.__init__() takes 1 positional argument but 6 were given
```

Pydantic models require **keyword arguments**.

---

### ✅ Fixed version

```python
# models.py — CORRECT
from pydantic import BaseModel

class Product(BaseModel):
    id: int
    name: str
    description: str
    price: float
    quantity: int
```

```python
# In main.py — use keyword arguments
products = [
    Product(id=1, name="Phone", description="Budget phone", price=99, quantity=10),
]
```

Pydantic also validates types automatically:
```python
Product(id="abc", name="Phone", description="x", price=99, quantity=10)
# ValidationError: id must be an integer
```

---

## 7. Database Config — `database.py`

---

### ❌ Buggy version

```python
# database.py — BROKEN
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# BUG 1: wrong DB URL format — missing the driver prefix
DB_URL = "localhost:5432/cisco"          # ← not a valid SQLAlchemy URL

# BUG 2: autocommit left as True (default)
SessionLocal = sessionmaker(
    autocommit=True,                     # ← with autocommit=True, every query auto-
    autoflush=True,                      #   commits, meaning you lose transaction control
    bind=create_engine(DB_URL)
)
```

**Error:**
```
sqlalchemy.exc.ArgumentError: Could not parse rfc1738 URL from string "localhost:5432/cisco"
```

Also, with `autocommit=True`, you cannot roll back failed transactions — dangerous in production.

---

### ✅ Fixed version

```python
# database.py — CORRECT
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Format: postgresql://username:password@host:port/database_name
DB_URL = "postgresql://postgres:12345678@localhost:5432/cisco"
#                      ↑ driver   ↑ user   ↑ password  ↑ port  ↑ db name

engine = create_engine(DB_URL)

SessionLocal = sessionmaker(
    autocommit=False,    # ← must be False so YOU control when to commit
    autoflush=False,
    bind=engine
)
```

> **Note for MySQL users:** Change the URL prefix to `mysql+mysqlconnector://` and the port to `3306`.

---

## 8. ORM Model — `database_models.py`

---

### ❌ Buggy version

```python
# database_models.py — BROKEN
from sqlalchemy import Column, Integer, String, Float
# BUG 1: missing declarative_base import
# from sqlalchemy.ext.declarative import declarative_base

# BUG 2: Base is never defined
class Product(Base):                    # ← NameError: name 'Base' is not defined
    __tablename__ = "product"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String)
    price = Column(Float)
    quantity = Column(Integer)
```

**Error:**
```
NameError: name 'Base' is not defined
```

Also — if you forget `__tablename__`, SQLAlchemy cannot map to any table:
```python
# Missing __tablename__ → SQLAlchemy error on startup
class Product(Base):
    # no __tablename__ = "product"
    id = Column(Integer, primary_key=True)
# sqlalchemy.exc.InvalidRequestError: Class 'Product' does not have a __tablename__
```

---

### ✅ Fixed version

```python
# database_models.py — CORRECT
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base   # ← must import this

Base = declarative_base()              # ← creates the base class for all ORM models

class Product(Base):
    __tablename__ = "product"          # ← tells SQLAlchemy which table to use

    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String)
    description = Column(String)
    price       = Column(Float)
    quantity    = Column(Integer)
```

> **Why two Product classes?**  
> `models.Product` (Pydantic) → validates data coming from the client  
> `database_models.Product` (SQLAlchemy) → represents a row in the database  
> They serve different purposes and **cannot replace each other**.

---

## 9. Database CRUD — `main.py`

---

### Create tables + seed data

#### ❌ Buggy version

```python
# main.py — BROKEN
import database_models
from database import engine, SessionLocal
from models import Product

app = FastAPI()

# BUG 1: creates tables but runs seed EVERY time server starts
database_models.Base.metadata.create_all(bind=engine)

def initiate_db():
    db = SessionLocal()
    seeds = [
        Product(id=1, name="Phone", description="Budget phone", price=99, quantity=10),
    ]
    for product in seeds:
        db.add(product)              # BUG 2: adding Pydantic object, not SQLAlchemy object
    db.commit()
    db.close()

initiate_db()   # ← runs every restart, duplicate IDs crash the app on 2nd run
```

**Error on second server start:**
```
sqlalchemy.exc.IntegrityError: duplicate key value violates unique constraint "product_pkey"
DETAIL: Key (id)=(1) already exists.
```

**Error from passing Pydantic object to db.add():**
```
sqlalchemy.orm.exc.UnmappedInstanceError: Class 'models.Product' is not mapped
```

#### ✅ Fixed version

```python
# main.py — CORRECT
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import database_models
from database import engine, SessionLocal
from models import Product

app = FastAPI()

database_models.Base.metadata.create_all(bind=engine)   # create tables once

def get_db():
    """Dependency — opens a DB session per request, always closes it after."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def initiate_db():
    db = SessionLocal()
    count = db.query(database_models.Product).count()
    if count == 0:                              # ← only seed when table is empty
        seeds = [
            Product(id=1, name="Phone",  description="Budget phone",  price=99,  quantity=10),
            Product(id=2, name="Laptop", description="Gaming laptop", price=999, quantity=6),
            Product(id=5, name="Pen",    description="Blue pen",      price=1,   quantity=100),
            Product(id=6, name="Table",  description="Office table",  price=299, quantity=20),
        ]
        for product in seeds:
            # .model_dump() → converts Pydantic object to dict
            # **  → unpacks dict into keyword args for SQLAlchemy constructor
            db.add(database_models.Product(**product.model_dump()))
        db.commit()
    db.close()

initiate_db()
```

---

### GET all products

#### ❌ Buggy version

```python
# main.py — BROKEN
@app.get("/products")
def get_all_products():
    # BUG: no DB session — where does db come from?
    db_products = db.query(database_models.Product).all()
    return db_products
```

**Error:**
```
NameError: name 'db' is not defined
```

#### ✅ Fixed version

```python
@app.get("/products")
def get_all_products(db: Session = Depends(get_db)):   # ← FastAPI injects the session
    return db.query(database_models.Product).all()
```

---

### GET one product by ID

#### ❌ Buggy version

```python
# main.py — BROKEN
@app.get("/products/{id}")
def get_product_by_id(id: int, db: Session = Depends(get_db)):
    db_product = db.query(database_models.Product).filter(
        database_models.Product.id == id
    ).first()
    return db_product    # BUG: returns None (Python null) if not found
                         # Frontend receives null with no explanation
```

**What the client receives when ID doesn't exist:**
```json
null
```

#### ✅ Fixed version

```python
@app.get("/products/{id}")
def get_product_by_id(id: int, db: Session = Depends(get_db)):
    db_product = db.query(database_models.Product).filter(
        database_models.Product.id == id
    ).first()
    if db_product:
        return db_product
    return "Product not found"    # ← explicit message when missing
```

---

### POST — add a product

#### ❌ Buggy version

```python
# main.py — BROKEN
@app.post("/products")
def add_product(product: Product, db: Session = Depends(get_db)):
    db_product = database_models.Product(**product.model_dump())
    db.add(db_product)
    # BUG: missing db.commit()
    return product
```

**What happens:** The product appears to be added (status 200), but when you fetch all products it's gone — the transaction was never committed and was silently rolled back when the session closed.

**No error message — just silent data loss.**

#### ✅ Fixed version

```python
@app.post("/products")
def add_product(product: Product, db: Session = Depends(get_db)):
    db_product = database_models.Product(**product.model_dump())
    db.add(db_product)
    db.commit()          # ← without this, nothing is actually saved
    return product
```

---

### PUT — update a product

#### ❌ Buggy version

```python
# main.py — BROKEN
@app.put("/products")                               # BUG: missing /{id} in URL path
def update_product(id: int, product: Product, db: Session = Depends(get_db)):
    db_product = db.query(database_models.Product).filter(
        database_models.Product.id == id
    ).first()
    if db_product:
        db_product.name = product.name
        db_product.description = product.description
        db_product.price = product.price
        db_product.quantity = product.quantity
        db.commit()
        return "Product updated successfully"
    return "Product not found"
```

**Error from frontend:**
```
405 Method Not Allowed   PUT http://localhost:8000/products
```

Without `{id}` in the path, FastAPI can't extract the ID from the URL, and the route doesn't match.

#### ✅ Fixed version

```python
@app.put("/products/{id}")                         # ← {id} must be in the path
def update_product(id: int, product: Product, db: Session = Depends(get_db)):
    db_product = db.query(database_models.Product).filter(
        database_models.Product.id == id
    ).first()
    if db_product:
        db_product.name        = product.name
        db_product.description = product.description
        db_product.price       = product.price
        db_product.quantity    = product.quantity
        db.commit()                                 # ← commit to persist changes
        return "Product updated successfully"
    return "Product not found"
```

---

### DELETE — remove a product

#### ❌ Buggy version

```python
# main.py — BROKEN
@app.delete("/products/{id}")
def delete_product(id: int, db: Session = Depends(get_db)):
    db_product = db.query(database_models.Product).filter(
        database_models.Product.id == id
    ).first()
    db.delete(db_product)   # BUG: no check if db_product is None
    db.commit()             # if id doesn't exist → db_product is None → crash
```

**Error when deleting a non-existent ID:**
```
sqlalchemy.orm.exc.UnmappedInstanceError: Class 'NoneType' is not mapped
```
or
```
Internal Server Error 500
```

#### ✅ Fixed version

```python
@app.delete("/products/{id}")
def delete_product(id: int, db: Session = Depends(get_db)):
    db_product = db.query(database_models.Product).filter(
        database_models.Product.id == id
    ).first()
    if db_product:              # ← always check before deleting
        db.delete(db_product)
        db.commit()
        return "Product deleted"
    return "Product not found"
```

---

## 10. CORS & Frontend Connection — `main.py`

The React app runs on port 3000. FastAPI runs on port 8000. Browsers block cross-origin requests by default.

---

### ❌ Buggy version — no CORS at all

```python
# main.py — BROKEN (no CORS middleware)
from fastapi import FastAPI
app = FastAPI()
# No CORS configuration
```

**Console error in browser (React app):**
```
Access to fetch at 'http://localhost:8000/products' from origin 'http://localhost:3000'
has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present.
```

GET requests may partially work in some browsers, but POST/PUT/DELETE will always fail.

---

### ❌ Buggy version — CORS origins only, methods missing

```python
# main.py — STILL BROKEN
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    # BUG: allow_methods not set → defaults to GET only
    # POST, PUT, DELETE are still blocked
)
```

**Console error when clicking Add / Edit / Delete in React:**
```
Method 'POST' not allowed by Access-Control-Allow-Methods
```

The products page loads (GET works), but add/edit/delete all fail silently or show errors.

---

### ❌ Buggy version — URL mismatch (`/product` vs `/products`)

```python
# main.py — BROKEN
@app.get("/product")          # ← singular: "product"
@app.post("/product")
@app.put("/product/{id}")
@app.delete("/product/{id}")
```

The React frontend calls `/products` (plural). FastAPI returns 404 for every request.

**Console error:**
```
404 Not Found   GET http://localhost:8000/products
404 Not Found   POST http://localhost:8000/products
```

---

### ✅ Fixed version — full working CORS + correct URLs

```python
# main.py — CORRECT
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # ← React dev server origin
    allow_methods=["*"],                      # ← allows GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],
)

# All routes use /products (plural) — matching what the React frontend calls
@app.get("/products")
@app.post("/products")
@app.put("/products/{id}")
@app.delete("/products/{id}")
```

---

## 11. Complete Final Files

All files below are correct and work together.

---

### `models.py`

```python
from pydantic import BaseModel

class Product(BaseModel):
    id: int
    name: str
    description: str
    price: float
    quantity: int
```

---

### `database.py`

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DB_URL = "postgresql://postgres:12345678@localhost:5432/cisco"

engine = create_engine(DB_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)
```

---

### `database_models.py`

```python
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Product(Base):
    __tablename__ = "product"

    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String)
    description = Column(String)
    price       = Column(Float)
    quantity    = Column(Integer)
```

---

### `main.py`

```python
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import database_models
from database import engine, SessionLocal
from models import Product

app = FastAPI()

# CORS — lets the React app (port 3000) call this API (port 8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create DB tables if they don't exist
database_models.Base.metadata.create_all(bind=engine)

# --- DB session dependency ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Seed data (runs once, only if table is empty) ---
def initiate_db():
    db = SessionLocal()
    if db.query(database_models.Product).count() == 0:
        seeds = [
            Product(id=1, name="Phone",  description="Budget phone",  price=99,  quantity=10),
            Product(id=2, name="Laptop", description="Gaming laptop", price=999, quantity=6),
            Product(id=5, name="Pen",    description="Blue pen",      price=1,   quantity=100),
            Product(id=6, name="Table",  description="Office table",  price=299, quantity=20),
        ]
        for p in seeds:
            db.add(database_models.Product(**p.model_dump()))
        db.commit()
    db.close()

initiate_db()

# --- Routes ---

@app.get("/")
def greet():
    return "Welcome to ListTrack"

@app.get("/products")
def get_all_products(db: Session = Depends(get_db)):
    return db.query(database_models.Product).all()

@app.get("/products/{id}")
def get_product_by_id(id: int, db: Session = Depends(get_db)):
    product = db.query(database_models.Product).filter(
        database_models.Product.id == id
    ).first()
    if product:
        return product
    return "Product not found"

@app.post("/products")
def add_product(product: Product, db: Session = Depends(get_db)):
    db.add(database_models.Product(**product.model_dump()))
    db.commit()
    return product

@app.put("/products/{id}")
def update_product(id: int, product: Product, db: Session = Depends(get_db)):
    p = db.query(database_models.Product).filter(
        database_models.Product.id == id
    ).first()
    if not p:
        return "Product not found"
    p.name        = product.name
    p.description = product.description
    p.price       = product.price
    p.quantity    = product.quantity
    db.commit()
    return "Product updated successfully"

@app.delete("/products/{id}")
def delete_product(id: int, db: Session = Depends(get_db)):
    p = db.query(database_models.Product).filter(
        database_models.Product.id == id
    ).first()
    if not p:
        return "Product not found"
    db.delete(p)
    db.commit()
    return "Product deleted"
```

---

## All Errors — Quick Reference

| File | Bug | Error Message | Fix |
|---|---|---|---|
| `main.py` | `print()` instead of `return` | Response body is `null` | Use `return` |
| `main.py` | `uvicorn main` (no app name) | `Import string must be in format <module>:<attribute>` | `uvicorn main:app --reload` |
| `models.py` | No `__init__` in plain class | `TypeError: Product() takes no arguments` | Add constructor with all fields |
| `models.py` | Positional args with Pydantic | `TypeError: __init__() takes 1 positional argument` | Use keyword args: `Product(id=1, name=...)` |
| `main.py` | `products[id-1]` for fetching | `IndexError` on non-sequential IDs | Loop and match `.id` attribute |
| `main.py` | Iterating list while deleting | Silent data skips / wrong deletion | Use `range(len())` and `del products[i]` |
| `database.py` | Wrong DB URL format | `Could not parse rfc1738 URL` | Use `postgresql://user:pass@host:port/db` |
| `database.py` | `autocommit=True` | Silent data loss / no rollback control | Set `autocommit=False` |
| `database_models.py` | Missing `declarative_base` import | `NameError: name 'Base' is not defined` | Import and call `declarative_base()` |
| `database_models.py` | Missing `__tablename__` | `InvalidRequestError: does not have __tablename__` | Add `__tablename__ = "product"` |
| `main.py` | `db.add(pydantic_object)` | `UnmappedInstanceError: not mapped` | Convert: `database_models.Product(**product.model_dump())` |
| `main.py` | Missing `db.commit()` | Silent data loss (status 200 but nothing saved) | Call `db.commit()` after every write |
| `main.py` | Seeding without empty-check | `IntegrityError: duplicate key value` | Add `if count == 0:` before seeding |
| `main.py` | `db.delete(None)` — no existence check | `UnmappedInstanceError: NoneType is not mapped` | Check `if db_product:` before deleting |
| `main.py` | No CORS middleware | `Blocked by CORS policy` in browser | Add `CORSMiddleware` |
| `main.py` | CORS without `allow_methods` | POST/PUT/DELETE blocked, only GET works | Add `allow_methods=["*"]` |
| `main.py` | `/product` vs `/products` mismatch | `404 Not Found` from frontend | Use `/products` consistently across all routes |
| `main.py` | Missing `{id}` in PUT/DELETE path | `405 Method Not Allowed` | Use `"/products/{id}"` in the decorator |

---

> Test all endpoints live at `http://localhost:8000/docs` — Swagger UI is built into FastAPI for free.
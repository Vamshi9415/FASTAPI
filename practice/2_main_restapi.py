from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.get("/")
def print_greet():
    return "Welcome to server"
from models import Product
products = [
            Product(id=1, name="Phone",  description="Budget phone",  price=99,  quantity=10),
            Product(id=2, name="Laptop", description="Gaming laptop", price=999, quantity=6),
            Product(id=5, name="Pen",    description="Blue pen",      price=1,   quantity=100),
            Product(id=6, name="Table",  description="Office table",  price=299, quantity=20)
]
@app.get("/products")
def get_all_products():
    #FastAPI (via Starlette) automatically serializes return values to JSON. When your endpoint returns Python dicts, lists,
    # or Pydantic models, FastAPI encodes them to JSON and sends them with Content-Type: application/json.
    return products 

@app.get("/products/{id}", response_model = Product)
# Using response_model=Product tells FastAPI to validate and serialize the endpoint output against the Product Pydantic schema—this enforces correct types, converts non-JSON-safe values, filters out any extra or private fields, generates accurate OpenAPI/Swagger response docs, and catches server-side shape errors so clients receive consistent, predictable JSON responses (use List[Product] for collections); the small validation/serialization cost is usually worth the safety, clarity, and documentation benefits.
def get_product_by_id(id:int):
    
    for prod in products :
        if prod.id == id:
            return prod
    
    raise HTTPException(
    status_code = 404,
    detail = "Product not found"
)
    
@app.post("/product")
def add_product(product : Product):
    if any(p.id == product.id for p in products):
        raise HTTPException(status_code = 400,detail = "Prodcut with this {product.id} is already present")
    products.append(product)
    return product
        
#curl request 
#Headers in a curl request tell the server extra information about the request — like what type of data you're sending, what format you expect, authentication details, etc.
# curl -X 'POST' -H "Content-Type: application/json" -d '{"id":4,"name":"titan","description":"nice watch","price":50,"quantity":3}' http://127.0.0.1:8000/product
# - curl: CLI HTTP client
# - -X 'POST': HTTP method (create)
# - -H "Content-Type: application/json": tell server body is JSON
# - -d '...': request body (JSON payload)
# - http://127.0.0.1:8000/product: endpoint URL

# PowerShell (preferred on Windows):
# Invoke-RestMethod -Method Post -Uri 'http://127.0.0.1:8000/product' -ContentType 'application/json' -Body '{"id":4,"name":"titan","description":"nice watch","price":50,"quantity":3}'
# - Invoke-RestMethod: native PowerShell HTTP helper (returns parsed JSON)
# - -Method Post / -Uri / -ContentType / -Body: same roles as curl flags
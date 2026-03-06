from fastapi import FastAPI, HTTPException, Depends
from database import session,engine
import database_models 
from models import Product
from sqlalchemy.orm import Session
app = FastAPI()

database_models.Base.metadata.create_all(bind = engine)

@app.get("/")
def print_greet():
    return "Welcome to server"
products = [
            Product(id=1, name="Phone",  description="Budget phone",  price=99,  quantity=10),
            Product(id=2, name="Laptop", description="Gaming laptop", price=999, quantity=6),
            Product(id=5, name="Pen",    description="Blue pen",      price=1,   quantity=100),
            Product(id=6, name="Table",  description="Office table",  price=299, quantity=20)
]
def get_db():
    db = session()
    try :
        yield db
    finally :
        db.close()


def init_db(db : Session):
    count = db.query(database_models.Product).count
    if count == 0:
        for product in products :

            db.add(database_models.Product(**product.model_dump())) # model_dump() converts a Pydantic model into a dictionary, and the ** operator unpacks that dictionary into keyword arguments so it can be passed to the SQLAlchemy model constructor.
            #unpacking means from a values from contaier like list tuple it spreads them out inot a indovidual variables
        db.commit()

with session() as db :
    init_db(db)
    
# with is like a context manager that automatically closes the db
# and equvalent to 
# db = session()

# try:
#     init_db(db)
# finally:
#     db.close()

#dependency injection is used only in fastapi routes
@app.get("/products")
def get_all_products(db : Session = Depends(get_db)): #here Depends(get_db) tells fastapi that this needs a get_db and automatically calls get_db and gets db sessions and pass to db
    db_products = db.query(database_models.Product).all()
    return db_products 

@app.get("/products/{id}", response_model = Product)
# Using response_model=Product tells FastAPI to validate and serialize the endpoint output against the Product Pydantic schema—this enforces correct types, converts non-JSON-safe values, filters out any extra or private fields, generates accurate OpenAPI/Swagger response docs, and catches server-side shape errors so clients receive consistent, predictable JSON responses (use List[Product] for collections); the small validation/serialization cost is usually worth the safety, clarity, and documentation benefits.
def get_product_by_id(id:int, db : Session = Depends(get_db)):
    
    product = db.query(database_models.Product).filter(database_models.Product.id == id).first()
    
    if not product :
        raise HTTPException(
    status_code = 404,
    detail = "Product not found"
)
    return product
    
@app.post("/product")
def add_product(product : Product,db : Session = Depends(get_db)):
    existing = db.query(database_models.Product).filter(database_models.Product.id == product.id).first()
    
    if existing :
        raise HTTPException(status_code = 400,detail = "Prodcut with this {product.id} is already present")
    
    db_product =database_models.Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product) #db.refresh(db_product) is used to reload the object from the database after committing, so that the Python object contains the latest values stored in the database.
    return db_product

#updating the product
@app.put("/product", response_model = Product)
def update_product(id :int, product: Product, db:Session = Depends(get_db)):
    db_prod = db.query(database_models.Product).filter(database_models.Product.id == id).first()
    
    if not db_prod :
        raise HTTPException(status_code = 404 ,detail = "Product Not Found")
    
    if db_prod :
        for key,value in product.model_dump().items():
            setattr(db_prod,key,value)
        #loop is same as 
        # db_prod.name = product.name
        # db_prod.description = product.description
        # db_prod.price = product.price
        # db_prod.quantity = product.quantity
    
    db.commit()
    db.refresh(db_prod)
    return db_prod

    

@app.delete("/product")
def delete_product(id : int, db: Session = Depends(get_db)):
    exist = db.query(database_models.Product).filter(database_models.Product.id == id).first()
    if not exist :
        raise HTTPException(status_code = 404 ,detail = "product not found")
    db.delete(exist)
    db.commit()
    return f"Product Deleted {id}"
    

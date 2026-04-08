from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List
import time

app = FastAPI()

# Create a simple endpoint /hello that returns "Hello, FastAPI!".
@app.get("/hello")
def greet() :
    return "HEllO WORLD"

# Define an endpoint /items/{item_id} that returns the item ID.

class product(BaseModel):
    id: int
    name: str
    price: float

products: List[product] = [
    product(id=1, name="Sample Product", price=9.99)
]

@app.get("/product/{id}", response_model = product)
def get_product_by_id(id: int):
    for prod in products :
        if prod.id == id :
            return prod
    raise HTTPException(status_code = 404, detail = "Product Not Found")

# Add an endpoint /search that accepts a query string like ?q=python
#adding search endpoint that accepts a query string ?q=python would require a function 
# that takes q 

@app.get("/search")
def search(q : str):
    return {
        "query" : q
    }

# Request Body
# Create a POST endpoint /users/ that accepts a JSON body with name and age.
# Return a confirmation message with the same data.


# BaseModel is a Pydantic class used in FastAPI to define and validate request/response
# data structures. It ensures type safety, automatic validation, and clean integration
# with FastAPI's auto-generated documentation."
class User(BaseModel):
    name : str
    age :int

#this is pydantic model User with structure like our request body name and age 
# FastApi automatically validates the incoming json against this model
# so endpoint can accepts the json body like this

# {
#   "name": "Vamshi",
#   "age": 24
# }

# In FastAPI, request bodies are defined using Pydantic models.
# You pass the model as a parameter to the endpoint function, and FastAPI automatically validates 
# and parses the JSON into that model. 
# You then access the fields from the model instance, not the class.

@app.post("/users/")
def post_users(user : User):
    return {
        "name" : user.name,
        "age" : user.age
    }

    

# Validation with Pydantic
# Define a User model with constraints (e.g., age > 0).
# Use it in your POST endpoint to validate input.

class UserModel(BaseModel):
    name : str 
    age :int = Field(...,gt = 0)
    # In Pydantic, Field(..., ...) uses ... to mark a field as required, meaning the client 
    # must provide it. Constraints like gt=0 enforce validation rules, so FastAPI automatically
    # rejects invalid input.
    
    nickname : Optional[str] = Field(None,max_length = 30, description = "Optional NickName")
    
    Salary : Optional[float] = Field(None, ge = 2000, le = 20000, description = "Salary must be in range 2k and 20k if provided")
 
@app.post("/create_user")
def create_user(user : UserModel):
    # add logic for adding user 
    
    return {"message": f"user {user.name} created successfully", "data" : user.dict()}
    
@app.post("/validate_age")
def validate_age(user : UserModel):
    #if age passes validation, return success
    
    return { "message" : f"Age validated for {user.age}"}
    #here no need to raise an exceptions because pydantic handles it


# Dependency Injection
# Write a dependency that checks if a user is authenticated (dummy check).
# Use it in an endpoint to restrict access.

# dependency injection is to supply external resources or logic to fucntions withut hardcoding them
# Declare the dependencies using Depends() fcutnion, FastAPI resolves them autiomatically

# its like a design pattern where you declare the dependencies like database Authentication logic that our endpoints
# needed and fastapi provides them when the function is called 


#dependency function

def authenticate_user(token :str = "secret"):
    if token != "secret" :
        raise HTTPException(status_code = 401, detail = "unauthorized")
    return token 

#endpoint using dependency 

@app.get("/secure_data")
def get_secure_data(token : str = Depends(authenticate_user)):
    return {"message" : "Access Granted !", "token": token} 
    
# Dependency function (authenticate_user)
# Checks if the provided token matches "secret-token".
# Raises HTTPException if not valid.
# Depends(authenticate_user)

# Tells FastAPI: "Before running get_secure_data, run authenticate_user and inject its result."
# If authentication fails, the endpoint won't execute.
# Endpoint (/secure-data/)
# Only accessible if the dependency passes.
# Returns a success message and the token.


# CRUD Simulation
# Build endpoints for:
# GET /books/ → list all books
# POST /books/ → add a book
# PUT /books/{id} → update a book
# DELETE /books/{id} → delete a book

class Book(BaseModel):
    id : int
    title : str
    author : str 

books : List[Book] = []

@app.get("/books/")
def get_books():
    return [book.dict() for book in books]

@app.post("/books/")
def add_book(book : Book):
    for b in books :
        if b.id == book.id :
            raise HTTPException(status_code = 400,
            detail = "Server cannot process the request due to client error")
    books.append(book)
    
    return {"message" : "Book added successfully", "book" : book} 

@app.put("/books/{id}")
def update_book(id : int, update_book : Book):
    for index,b in enumerate(books) :
        if b.id == id :
            books[index] = update_book
            return {"message" : "Book updated successfully", "book" : update_book}
    raise HTTPException(status_code = 404, detail = "Book Not Found")
    

@app.delete("/books/{id}")
def delete_book(id: int):
    for index, b in enumerate(books):
        if b.id == id:
            deleted_book = books.pop(index)
            return {"message": "Book deleted successfully", "book": deleted_book}
    raise HTTPException(status_code=404, detail="Book not found")

    

# Middleware
# Add a middleware that logs request time.
# Print the method and path for each request.

# middleware : middleware is a function that runs before and after every request. It sits between
# client request and your endpoint logic , allowing you to add cross cutting behaviour such as 
# logging, authentication, performance monitoring or modifying requests/responses

# what does middleware do 
# It intercepts requests before they reach our endpoints 
# Runs code after responses are generated, before they are sent back to the client

from fastapi import Request
import asyncio
@app.middleware('http')
async def log_requests(request : Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    
    duration = time.time() - start_time 
    response.headers["X-Process-Time"] = str(duration)
    print(f" Request : {request.url} completed in {duration :.4f} seconds")
    
    return response 

# Origin = combination of scheme (http/https), domain, and port.
# Example:
# https://example.com:443 → one origin
# http://example.com:80 → different origin (because of scheme/port).

# Why CORS exists:  
# Browsers block cross-origin requests by default to prevent malicious sites from stealing data from another site.
# Server-side role:
# The server decides whether to allow requests from other origins by sending special HTTP headers (like Access-Control-Allow-Origin).
# If the server includes the right CORS headers, the browser allows the request.
# If not, the browser blocks it.
# So yes — CORS is enforced by the browser, but controlled by the server. The check happens client-side (browser), but the server must explicitly permit or deny cross-origin access.

# Static Files
# Serve a static folder (e.g., /static) with images or CSS.
# Access via http://localhost:8000/static/filename.

# to access the static files in fastapi use StaticFiles class from fastapi.staticfiles and mount it to a path, so that through localhost we can access it

from fastapi.staticfiles import StaticFiles
import os

#mount the static directory

os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"),name = "static")

@app.get("/")
def root():
    return {"message" : "Go to /static/file_name to access static files" }



# Simple Authentication
# Create a login endpoint that accepts username/password.
# Return a fake JWT token (string) for practice.

class LoginRequest(BaseModel):
    username : str 
    password : str 

@app.post("/login")
def login(request : LoginRequest) :
    
    #dummy check 
    if request.username == "username" and request.password == "password" :
        fake_token = "fake_jwt_token"
        
        return {
            "Acess-token" : fake_token ,
            "token_type " : "bearer"
        }
    else :
        raise HTTPException(status_code = 401, detail =" INvalid Username ot password")
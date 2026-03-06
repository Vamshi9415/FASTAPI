# Pydantic's BaseModel is used for data validation and parsing in FastAPI.
# It ensures that the data you receive (e.g., from API requests) matches the expected types and structure.
# If the incoming data is invalid (wrong type, missing fields), FastAPI will automatically return an error response.
# This helps prevent bugs, improves security, and makes your API more robust.
# If you don't use Pydantic models, you would have to manually validate and parse all incoming data, which is error-prone and tedious.

from pydantic import BaseModel

class Product(BaseModel):
    id: int         # Ensures 'id' is always an integer
    name: str       # Ensures 'name' is always a string
    description: str       # Ensures 'desc' is always a string
    price: float    # Ensures 'price' is always a float
    quantity: int   # Ensures 'quantity' is always an integer
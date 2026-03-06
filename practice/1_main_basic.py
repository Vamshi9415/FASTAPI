from fastapi import FastAPI

# create a objct of fastapi
app = FastAPI()

@app.get("/")
def print_greet():
    return "Welcome to server"

# 1. how to run this server 
# using uvicorn which is a web server uvicorn filename:object_name --reload  python -m uvicorn 1_main:app --reload 




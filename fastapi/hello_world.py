"""
01 - Hello World
================
The simplest possible FastAPI app: one GET route that returns a greeting.

Run:  uvicorn fastapi.hello_world:app --reload
Docs: http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def greet():
    return "Welcome to the server"

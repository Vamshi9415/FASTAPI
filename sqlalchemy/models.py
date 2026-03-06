"""
models.py — SQLAlchemy ORM models
==================================
Each class here maps to a table in the database.
`Base` is the declarative base that SQLAlchemy uses to track all models.
"""

from sqlalchemy import Column, Float, Integer, String
from sqlalchemy.orm import declarative_base

# declarative_base() creates the registry that connects ORM classes to DB tables.
Base = declarative_base()


class Product(Base):
    __tablename__ = "product"

    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String,  nullable=False)
    description = Column(String)
    price       = Column(Float,   nullable=False)
    quantity    = Column(Integer, nullable=False)

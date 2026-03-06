from sqlalchemy.ext.declarative import declarative_base
#Creates a base class you use to define ORM models.
# Think of it as the root that tells SQLAlchemy "these classes map to database tables."

from sqlalchemy import Column, Integer, String, Float

Base = declarative_base()
#Base is the class you inherit from when making table-mapping classes (like Product).
class Product(Base):
    
    __tablename__ = "product"
    id = Column(Integer,primary_key = True, index = True)        
    name = Column(String)       
    description = Column(String)       
    price = Column(Float)   
    quantity = Column(Integer) 
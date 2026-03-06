from sqlalchemy.orm import sessionmaker

from sqlalchemy import create_engine
#create engine creates the databse connection manager that handles the database connection like a database gateway


#
# 
#   from sqlalchemy import create_engine
#   engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={...})
#   SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#   bind is the database Engine the session talks to; autoflush (True by default) makes the session automatically send 
# pending changes to the DB before running a query so queries see up-to-date data; autocommit (should be False) controls whether the session manages a transaction automatically—keeping it False and calling commit() explicitly is safer. Use SessionLocal = sessionmaker(bind=engine,
# autocommit=False, autoflush=False) in real apps so you control when writes are flushed and committed.

# Here we keep the default factory so callers can configure/bind an engine elsewhere.
import os
from urllib.parse import quote_plus

user = os.getenv("POSTGRES_USER", "postgres")
pw = quote_plus(os.getenv("POSTGRES_PASSWORD", "root"))   # encodes special chars
host = os.getenv("POSTGRES_HOST", "localhost")
port = os.getenv("POSTGRES_PORT", "5432")
db = os.getenv("POSTGRES_DB", "Product")

DATABASE_URL = f"postgresql://{user}:{pw}@{host}:{port}/{db}" #postgresql://USER:PASSWORD@HOST:PORT/DBNAME
engine = create_engine(DATABASE_URL)
session = sessionmaker(
    autoflush=False,
    autocommit=False,
    bind=engine
)
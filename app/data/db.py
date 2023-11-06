from sqlalchemy import (
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base

# Create a base class for declarative class definitions
Base = declarative_base()

# create file data.db
engine = create_engine("sqlite:///data.db")

Base.metadata.create_all(engine)

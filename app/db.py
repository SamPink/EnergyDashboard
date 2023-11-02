from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    Float,
    String,
    DateTime,
    ForeignKey,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Create a base class for declarative class definitions
Base = declarative_base()


# Define the Period model
class Period(Base):
    __tablename__ = "periods"

    id = Column(Integer, primary_key=True)
    start = Column(DateTime, nullable=False)
    end = Column(DateTime, nullable=False)
    carbon_intensity = Column(Float)
    settlement_period = Column(Integer)

    # Relationships
    demand = relationship("Demand", back_populates="period", uselist=False)
    generation = relationship("Generation", back_populates="period", uselist=False)
    energy_types = relationship("EnergyType", back_populates="period")


# Define the Demand model
class Demand(Base):
    __tablename__ = "demands"

    id = Column(Integer, primary_key=True)
    period_id = Column(Integer, ForeignKey("periods.id"))
    net = Column(Float)
    gross = Column(Float)
    pumped_storage = Column(Float)
    exports = Column(Float)
    station_load = Column(Float)
    embedded_wind = Column(Float)
    embedded_solar = Column(Float)
    actual_net = Column(Float)
    actual_gross = Column(Float)

    # Relationship
    period = relationship("Period", back_populates="demand")


# Define the Generation model
class Generation(Base):
    __tablename__ = "generations"

    id = Column(Integer, primary_key=True)
    period_id = Column(Integer, ForeignKey("periods.id"))
    total = Column(Float)

    # Relationship
    period = relationship("Period", back_populates="generation")


# Define the EnergyType model
class EnergyType(Base):
    __tablename__ = "energy_types"

    id = Column(Integer, primary_key=True)
    period_id = Column(Integer, ForeignKey("periods.id"))
    type_name = Column(String)
    total = Column(Float)
    percentage = Column(Float)

    # Relationship
    period = relationship("Period", back_populates="energy_types")


# Create an in-memory SQLite database
engine = create_engine("sqlite:///:memory:")

# Create all tables in the engine
Base.metadata.create_all(engine)

# Create a session to interact with the database
Session = sessionmaker(bind=engine)
session = Session()

# Now the database and tables are set up in memory
# Next, we would populate it with data from our JSON file

# Since the database is in memory, it will not persist after this session ends
# To have a persistent database, we would use a file-based SQLite database or another database server

# Placeholder for data insertion, which we'll do next
"Models defined and database schema created in memory."

# Confirming if tables were created
print(engine.table_names())

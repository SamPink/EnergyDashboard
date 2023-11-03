from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    Float,
    String,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

import dateutil.parser

# Create a base class for declarative class definitions
Base = declarative_base()

# create file data.db
engine = create_engine("sqlite:///data.db")


# Define the Period model
class Period(Base):
    __tablename__ = "periods"

    id = Column(Integer, primary_key=True)
    start = Column(DateTime, nullable=False)
    end = Column(DateTime, nullable=False)
    carbon_intensity = Column(Float)
    settlement_period = Column(Integer)

    UniqueConstraint("start", "end", name="uix_start_end")

    # Relationships
    demand = relationship("Demand", back_populates="period", uselist=False)
    generation = relationship("Generation", back_populates="period", uselist=False)
    energy_types = relationship("EnergyType", back_populates="period")

    @classmethod
    def from_dict(cls, data):
        return cls(
            start=dateutil.parser.isoparse(data["start"]),
            end=dateutil.parser.isoparse(data["end"]),
            carbon_intensity=data["carbonIntensity"],
            settlement_period=data["settlementPeriod"],
        )


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

    @classmethod
    def from_dict(cls, data, period):
        return cls(
            period=period,
            net=data["demandNet"],
            gross=data["demandGross"],
            pumped_storage=data["pumpedStorage"],
            exports=data["exports"],
            station_load=data["stationLoad"],
            embedded_wind=data["embeddedWind"],
            embedded_solar=data["embeddedSolar"],
            actual_net=data["actualNet"],
            actual_gross=data["actualGross"],
        )


# Define the Generation model
class Generation(Base):
    __tablename__ = "generations"

    id = Column(Integer, primary_key=True)
    period_id = Column(Integer, ForeignKey("periods.id"))
    total = Column(Float)

    # Relationship
    period = relationship("Period", back_populates="generation")

    @classmethod
    def from_dict(cls, data, period):
        return cls(
            period=period,
            total=data["generationTotal"],
        )


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

    @classmethod
    def from_dict(cls, data, period):
        return [
            cls(
                period=period,
                type_name=gen_type,
                total=values["total"],
                percentage=values["percentage"],
            )
            for gen_type, values in data.items()
        ]


if __name__ == "__main__":
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Confirming if tables were created
    print(engine.table_names())

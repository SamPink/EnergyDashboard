from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

import dateutil.parser

from .db import Base

import datetime


# Define the Period model
class Period(Base):
    __tablename__ = "periods"
    id = Column(Integer, primary_key=True)
    start = Column(DateTime, nullable=False)
    end = Column(DateTime, nullable=False)
    carbon_intensity = Column(Float)
    settlement_period = Column(Integer)
    UniqueConstraint("start", "end", name="uix_start_end")
    generation = relationship("Generation", back_populates="period", uselist=False)
    energy_types = relationship("EnergyType", back_populates="period")

    @classmethod
    def from_dict(cls, data):
        return cls(
            start=dateutil.parser.isoparse(data["start"]),
            end=dateutil.parser.isoparse(data["end"]),
            carbon_intensity=data.get("carbonIntensity"),
            settlement_period=data.get("settlementPeriod"),
        )


# Define the Generation model
class Generation(Base):
    __tablename__ = "generations"
    id = Column(Integer, primary_key=True)
    period_id = Column(Integer, ForeignKey("periods.id"))
    total = Column(Float)
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


class Weather(Base):
    __tablename__ = "weather"
    id = Column(Integer, primary_key=True)
    time_epoch = Column(Integer)
    time = Column(DateTime, unique=True)
    # add a prediction column defult to default to 0
    preiction = Column(Integer, default=0)
    temp_c = Column(Float)
    temp_f = Column(Float)
    is_day = Column(Integer)
    condition_text = Column(String)
    condition_icon = Column(String)
    condition_code = Column(Integer)
    wind_mph = Column(Float)
    wind_kph = Column(Float)
    wind_degree = Column(Integer)
    wind_dir = Column(String)
    pressure_mb = Column(Float)
    pressure_in = Column(Float)
    precip_mm = Column(Float)
    precip_in = Column(Float)
    humidity = Column(Integer)
    cloud = Column(Integer)
    feelslike_c = Column(Float)
    feelslike_f = Column(Float)
    windchill_c = Column(Float)
    windchill_f = Column(Float)
    heatindex_c = Column(Float)
    heatindex_f = Column(Float)
    dewpoint_c = Column(Float)
    dewpoint_f = Column(Float)
    will_it_rain = Column(Integer)
    chance_of_rain = Column(Integer)
    will_it_snow = Column(Integer)
    chance_of_snow = Column(Integer)
    vis_km = Column(Float)
    vis_miles = Column(Float)
    gust_mph = Column(Float)
    gust_kph = Column(Float)
    uv = Column(Float)

    @classmethod
    def from_dict(cls, data):
        return cls(
            time_epoch=data["time_epoch"],
            time=datetime.datetime.strptime(data["time"], "%Y-%m-%d %H:%M"),
            temp_c=data["temp_c"],
            temp_f=data["temp_f"],
            is_day=data["is_day"],
            condition_text=data["condition"]["text"],
            condition_icon=data["condition"]["icon"],
            condition_code=data["condition"]["code"],
            wind_mph=data["wind_mph"],
            wind_kph=data["wind_kph"],
            wind_degree=data["wind_degree"],
            wind_dir=data["wind_dir"],
            pressure_mb=data["pressure_mb"],
            pressure_in=data["pressure_in"],
            precip_mm=data["precip_mm"],
            precip_in=data["precip_in"],
            humidity=data["humidity"],
            cloud=data["cloud"],
            feelslike_c=data["feelslike_c"],
            feelslike_f=data["feelslike_f"],
            windchill_c=data["windchill_c"],
            windchill_f=data["windchill_f"],
            heatindex_c=data["heatindex_c"],
            heatindex_f=data["heatindex_f"],
            dewpoint_c=data["dewpoint_c"],
            dewpoint_f=data["dewpoint_f"],
            will_it_rain=data["will_it_rain"],
            chance_of_rain=data["chance_of_rain"],
            will_it_snow=data["will_it_snow"],
            chance_of_snow=data["chance_of_snow"],
            vis_km=data["vis_km"],
            vis_miles=data["vis_miles"],
            gust_mph=data["gust_mph"],
            gust_kph=data["gust_kph"],
            uv=data["uv"],
        )

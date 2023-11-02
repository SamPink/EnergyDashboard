import requests
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
from db import Base, Period, Demand, Generation, EnergyType

from datetime import datetime
import dateutil.parser

# Database setup - replace 'sqlite:///generation.db' with your database URI
engine = create_engine("sqlite:///generation.db")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

# Extract: Fetch data from the API
url = "https://www.energydashboard.co.uk/api/today/generation"
response = requests.get(url)
data = response.json()

# Transform: Validate and structure the data
# Assuming the JSON keys match the model attributes exactly
half_hourly_data = data["halfHourlyData"]

# Load: Insert data into the database
session = Session()
try:
    for entry in half_hourly_data:
        start_time = dateutil.parser.isoparse(entry["start"])
        end_time = dateutil.parser.isoparse(entry["end"])

        # Check if the period already exists in the database
        period = (
            session.query(Period)
            .filter(and_(Period.start == start_time, Period.end == end_time))
            .first()
        )

        if period is None:
            period = Period(
                start=start_time,
                end=end_time,
                carbon_intensity=entry["carbonIntensity"],
                settlement_period=entry["settlementPeriod"],
            )
            session.add(period)
            session.flush()  # This will assign an ID to the period without committing the transaction

            demand = Demand(
                period_id=period.id,
                net=entry["demandValues"]["demandNet"],
                gross=entry["demandValues"]["demandGross"],
                pumped_storage=entry["demandValues"]["pumpedStorage"],
                exports=entry["demandValues"]["exports"],
                station_load=entry["demandValues"]["stationLoad"],
                embedded_wind=entry["demandValues"]["embeddedWind"],
                embedded_solar=entry["demandValues"]["embeddedSolar"],
                actual_net=entry["demandValues"]["actualNet"],
                actual_gross=entry["demandValues"]["actualGross"],
            )
            session.add(demand)

            generation = Generation(period_id=period.id, total=entry["generationTotal"])
            session.add(generation)

            for gen_type, values in entry["generationValues"].items():
                energy_type = EnergyType(
                    period_id=period.id,
                    type_name=gen_type,
                    total=values["total"],
                    percentage=values["percentage"],
                )
                session.add(energy_type)

            # Commit the transaction
            session.commit()
except Exception as e:
    session.rollback()
    raise e
finally:
    session.close()

print("ETL process completed.")

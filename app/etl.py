import requests
import logging
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
from db import Base, Period, Demand, Generation, EnergyType, engine
from datetime import datetime
import dateutil.parser

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


def extract(url):
    response = requests.get(url)
    data = response.json()
    return data["halfHourlyData"]


def transform(half_hourly_data):
    transformed_data = []
    for entry in half_hourly_data:
        transformed_entry = {
            "period": Period.from_dict(entry),
            "demand": Demand.from_dict(
                entry["demandValues"], None
            ),  # period will be updated in load step
            "generation": Generation.from_dict(
                entry, None
            ),  # period will be updated in load step
            "energy_types": EnergyType.from_dict(
                entry["generationValues"], None
            ),  # period will be updated in load step
        }
        transformed_data.append(transformed_entry)
    return transformed_data


def load(transformed_data):
    session = Session()
    try:
        for entry in transformed_data:
            period = (
                session.query(Period)
                .filter(
                    and_(
                        Period.start == entry["period"].start,
                        Period.end == entry["period"].end,
                    )
                )
                .first()
            )
            if period is None:
                period = entry["period"]
                session.add(period)
                session.flush()  # This will assign an ID to the period without committing the transaction

            entry["demand"].period = period
            entry["generation"].period = period
            for energy_type in entry["energy_types"]:
                energy_type.period = period

            session.add(entry["demand"])
            session.add(entry["generation"])
            session.add_all(entry["energy_types"])

            # Commit the transaction
            session.commit()

        # Log the number of new rows added
        new_rows_count = len(session.new)
        logger.info(f"New rows added: {new_rows_count}")
    except Exception as e:
        session.rollback()
        logger.exception("An error occurred while loading data into the database.")
        raise e
    finally:
        session.close()


def etl_process(url):
    data = extract(url)
    transformed_data = transform(data)
    load(transformed_data)
    print("ETL process completed.")


if __name__ == "__main__":
    url = "https://www.energydashboard.co.uk/api/today/generation"
    etl_process(url)

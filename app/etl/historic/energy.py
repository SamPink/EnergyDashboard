import datetime
import requests
import logging
from sqlalchemy import and_
from sqlalchemy.orm import sessionmaker

import json

from ...data.models import Period, Generation, EnergyType
from ...data.db import Base, engine


def get_history(days: int):
    # https://www.energydashboard.co.uk/api/historical/generation?from_date=2023-08-10T23:00:00Z&to_date=2023-11-08T23:59:59Z&group_by=1d

    base_url = "https://www.energydashboard.co.uk/api/historical/generation"

    today = datetime.datetime.now()

    from_date = today - datetime.timedelta(days=days)

    from_date = from_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    to_date = today.strftime("%Y-%m-%dT%H:%M:%SZ")

    params = {"from_date": from_date, "to_date": to_date, "group_by": "1d"}

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()

        return response.json()
    except requests.exceptions.HTTPError as e:
        logging.error(e)
        raise e


def run(days=90):
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)

    data = get_history(days)

    half_hourly_data_historic_sample = data.get("halfHourlyData")

    # create db session
    with Session() as session:
        for period in half_hourly_data_historic_sample:
            period_instance = Period.from_dict(period)
            generation_instance = Generation.from_dict(period, period_instance)
            energy_type_instances = EnergyType.from_dict(
                period["generationValues"], period_instance
            )
            session.add(period_instance)
            session.add(generation_instance)
            session.add_all(energy_type_instances)

        session.commit()

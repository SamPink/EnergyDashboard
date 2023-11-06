import requests
import logging
from sqlalchemy import and_
from sqlalchemy.orm import sessionmaker

import json

from ...data.models import Period, Generation, EnergyType
from ...data.db import Base, engine


def run():
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)

    # get the folder of this file
    import os

    path = os.path.dirname(os.path.abspath(__file__))

    # read history from file generation (1).json from this folder
    with open(path + "/generation (1).json") as f:
        data = json.load(f)

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

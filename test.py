from app.etl.energy import run
from app.etl.weather import run as run_weather

from app.etl.historic.energy import run as run_historic
from app.etl.historic.weather import run as run_historic_weather

from app.data.db import Base, engine

Base.metadata.create_all(engine)

run_historic_weather()

run_historic()

run()

run_weather()

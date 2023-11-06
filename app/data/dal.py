from sqlalchemy import func
from .models import Period, EnergyType, Weather


class DataAccessLayer:
    def __init__(self, session):
        self.session = session

    def get_carbon_intensity_over_time(self):
        """Retrieve carbon intensity over time."""
        return self.session.query(Period.start, Period.carbon_intensity).all()

    """ def get_total_demand_and_generation_over_time(self):
        
        return (
            self.session.query(
                Period.start,
                func.sum(Demand.net).label("total_demand"),
                func.sum(Generation.total).label("total_generation"),
            )
            .join(Demand)
            .join(Generation)
            .group_by(Period.start)
            .all()
        ) """

    def get_energy_mix(self, specific_time=None):
        """Retrieve energy mix."""
        query = (
            self.session.query(
                EnergyType.type_name,
                func.sum(EnergyType.total).label("total_generation"),
            )
            .join(Period)
            .group_by(EnergyType.type_name)
        )

        if specific_time:
            query = query.filter(
                Period.start <= specific_time, Period.end > specific_time
            )

        return query.all()

    """ def get_demand_breakdown(self):
        
        return (
            self.session.query(
                Period.start,
                Demand.net,
                Demand.gross,
                Demand.pumped_storage,
                Demand.exports,
                Demand.station_load,
                Demand.embedded_wind,
                Demand.embedded_solar,
                Demand.actual_net,
                Demand.actual_gross,
            )
            .join(Demand)
            .all()
        ) """

    def get_weather(self):
        return self.session.query(
            Weather.time,
            Weather.temp_c,
            Weather.wind_mph,
            Weather.wind_dir,
            Weather.pressure_mb,
            Weather.humidity,
            Weather.gust_mph,
        ).all()

    def get_wind_data(self):
        """Retrieve wind speed and wind energy generation."""
        wind_speed = (
            self.session.query(
                func.strftime("%H", Weather.time).label("hour"),
                func.avg(Weather.wind_mph).label("wind_speed"),
            )
            .filter(
                func.strftime("%Y-%m-%d", Weather.time)
                == func.strftime("%Y-%m-%d", func.current_date())
            )
            .filter(func.strftime("%H:%M:%S", Weather.time) <= "14:00:00")
            .group_by("hour")
        ).subquery()

        wind_generation = (
            self.session.query(
                func.strftime("%H", Period.start).label("hour"),
                func.sum(EnergyType.total).label("wind_generation"),
            )
            .join(EnergyType)
            .filter(EnergyType.type_name == "Wind")
            .filter(
                func.strftime("%Y-%m-%d", Period.start)
                == func.strftime("%Y-%m-%d", func.current_date())
            )
            .group_by("hour")
        ).subquery()

        # Now, we join the subqueries on the hour column to combine the data
        wind_data = (
            self.session.query(
                wind_speed.c.hour,
                wind_speed.c.wind_speed,
                wind_generation.c.wind_generation,
            )
            .join(wind_generation, wind_speed.c.hour == wind_generation.c.hour)
            .all()
        )

        return wind_data

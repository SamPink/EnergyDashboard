from sqlalchemy import func
from db import Period, Demand, Generation, EnergyType


class DataAccessLayer:
    def __init__(self, session):
        self.session = session

    def get_carbon_intensity_over_time(self):
        return self.session.query(Period.start, Period.carbon_intensity).all()

    def get_total_demand_and_generation_over_time(self):
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
        )

    def get_energy_mix(self, specific_time=None):
        query = self.session.query(
            EnergyType.type_name, func.sum(EnergyType.total).label("total_generation")
        ).group_by(EnergyType.type_name)
        if specific_time:
            query = query.filter(
                Period.start <= specific_time, Period.end > specific_time
            )
        return query.all()

    def get_demand_breakdown(self):
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
        )

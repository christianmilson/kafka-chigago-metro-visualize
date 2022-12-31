"""Defines trends calculations for stations"""
import logging

import faust


logger = logging.getLogger(__name__)


# Faust will ingest records from Kafka in this format
class Station(faust.Record):
    stop_id: int
    direction_id: str
    stop_name: str
    station_name: str
    station_descriptive_name: str
    station_id: int
    order: int
    red: bool
    blue: bool
    green: bool


# Faust will produce records to Kafka in this format
class TransformedStation(faust.Record):
    station_id: int
    station_name: str
    order: int
    line: str


app = faust.App("stations-stream", broker="kafka://localhost:9092", store="memory://")
topic = app.topic("stations_db_stations", value_type=Station)
out_topic = app.topic("org.chicago.cta.stations.table.v1", partitions=1)
table = app.Table(
   "stations",
   default=int,
   partitions=1,
   changelog_topic=out_topic,
)

@app.agent(topic)
async def transformed_stations(stations):
    async for station in stations:
        line = 'green'
        if station.red:
            line = 'red'
        elif station.blue:
            line = 'blue'

        transformed = TransformedStation(
            station_id=station.station_id,
            station_name=station.station_name,
            order=station.order,
            line=line,
        )

        table[transformed.station_id] = transformed
        print('processed station_id: ' + str(transformed.station_id))


if __name__ == "__main__":
    app.main()

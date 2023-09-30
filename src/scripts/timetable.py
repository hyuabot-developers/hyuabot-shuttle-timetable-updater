import asyncio
import csv
from datetime import datetime, timedelta

from aiohttp import ClientSession
from sqlalchemy import insert
from sqlalchemy.orm import Session

from models import ShuttleTimetable, ShuttleRouteStop, ShuttleRoute


async def insert_shuttle_timetable(db_session: Session):
    term_keys = ["semester", "vacation", "vacation_session"]
    day_keys = ["week", "weekend"]

    tasks = []
    db_session.query(ShuttleTimetable).delete()
    for term in term_keys:
        for day in day_keys:
            tasks.append(fetch_shuttle_timetable(db_session, term, day))
    await asyncio.gather(*tasks)
    db_session.commit()


async def fetch_shuttle_timetable(db_session: Session, period: str, day: str):
    base_url = "https://raw.githubusercontent.com/hyuabot-developers/hyuabot-shuttle-timetable/feat/v2"
    url = f"{base_url}/{period}/{day}.csv"
    day_dict = {"week": "weekdays", "weekend": "weekends"}
    timetable: list[dict] = []

    route_dict: dict[str, dict] = {}
    for route_item in db_session.query(ShuttleRoute).all():  # type: ShuttleRoute
        if route_item.route_tag not in route_dict:
            route_dict[route_item.route_tag] = {}
        route_dict[route_item.route_tag][(route_item.start_stop, route_item.end_stop)] = route_item.route_name
    async with ClientSession() as session:
        async with session.get(url) as response:
            reader = csv.reader((await response.text()).splitlines(), delimiter=",")
            for shuttle_type, shuttle_time, shuttle_start_stop, shuttle_end_stop in reader:
                route_name = route_dict[shuttle_type][(shuttle_start_stop, shuttle_end_stop)]
                timetable.append(
                    dict(
                        route_name=route_name,
                        period_type=period,
                        weekday=day_dict[day] == "weekdays",
                        departure_time=f'{shuttle_time} +09:00',
                    ),
                )
    insert_statement = insert(ShuttleTimetable).values(timetable)
    db_session.execute(insert_statement)
    db_session.commit()

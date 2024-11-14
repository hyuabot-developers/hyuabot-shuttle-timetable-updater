import asyncio
import csv

from aiohttp import ClientTimeout, ClientSession
from sqlalchemy import insert
from sqlalchemy.orm import Session

from models import ShuttleRouteStop


async def get_route_stop_list(db_session: Session) -> None:
    route_stop_list: list[dict] = []
    try:
        url = "https://raw.githubusercontent.com/hyuabot-developers/hyuabot-shuttle-timetable" \
              "/feat/v2/shuttle/route_stop.csv"
        timeout = ClientTimeout(total=3.0)
        async with ClientSession(timeout=timeout) as session:
            async with session.get(url) as response:
                reader = csv.reader((await response.text()).splitlines())
                for route_name, stop_name, stop_order, cumulative_time in reader:
                    route_stop_list.append({
                        "route_name": route_name,
                        "stop_name": stop_name,
                        "stop_order": stop_order,
                        "cumulative_time": int(cumulative_time),
                    })
    except asyncio.exceptions.TimeoutError:
        print("TimeoutError")
    except AttributeError:
        print("AttributeError", url)
    db_session.execute(insert(ShuttleRouteStop).values(route_stop_list))
    db_session.commit()

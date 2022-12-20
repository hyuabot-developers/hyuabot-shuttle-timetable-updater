import asyncio
import csv

from aiohttp import ClientTimeout, ClientSession
from sqlalchemy import insert
from sqlalchemy.orm import Session

from models import ShuttleRoute


async def get_route_list(db_session: Session) -> None:
    route_list: list[dict] = []
    try:
        url = "https://raw.githubusercontent.com/hyuabot-developers/hyuabot-shuttle-timetable/feat/v2/shuttle/route.csv"
        timeout = ClientTimeout(total=3.0)
        async with ClientSession(timeout=timeout) as session:
            async with session.get(url) as response:
                reader = csv.reader((await response.text()).splitlines())
                for route_name, description_korean, description_english, tag, start_stop, end_stop in reader:
                    route_list.append({
                        "route_name": route_name,
                        "route_description_korean": description_korean,
                        "route_description_english": description_english,
                        "route_tag": tag,
                        "start_stop": start_stop,
                        "end_stop": end_stop,
                    })
    except asyncio.exceptions.TimeoutError:
        print("TimeoutError")
    except AttributeError:
        print("AttributeError", url)
    db_session.execute(insert(ShuttleRoute).values(route_list))
    db_session.commit()

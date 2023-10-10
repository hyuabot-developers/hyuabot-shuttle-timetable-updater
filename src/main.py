import asyncio

from sqlalchemy import delete, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker

from models import ShuttleRoute, ShuttleRouteStop, ShuttleTimetable
from scripts.route import get_route_list
from scripts.route_stop import get_route_stop_list
from scripts.timetable import insert_shuttle_timetable
from utils.database import get_db_engine, get_master_db_engine


async def main():
    connection = get_db_engine()
    session_constructor = sessionmaker(bind=connection)
    session = session_constructor()
    if session is None:
        raise RuntimeError("Failed to get db session")
    try:
        await execute_script(session)
    except OperationalError:
        connection = get_master_db_engine()
        session_constructor = sessionmaker(bind=connection)
        session = session_constructor()
        await execute_script(session)


async def execute_script(session):
    drop_seq = \
        text("alter sequence shuttle_timetable_seq_seq restart with 1;")
    session.execute(delete(ShuttleTimetable))
    session.execute(drop_seq)
    session.execute(delete(ShuttleRouteStop))
    session.execute(delete(ShuttleRoute))
    await get_route_list(session)
    await get_route_stop_list(session)
    await insert_shuttle_timetable(session)
    session.close()

if __name__ == '__main__':
    asyncio.run(main())

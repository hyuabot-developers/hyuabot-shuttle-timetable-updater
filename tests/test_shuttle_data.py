import datetime

import pytest
from sqlalchemy import Engine, delete
from sqlalchemy.orm import Session, sessionmaker

from models import BaseModel, ShuttleRoute, ShuttleRouteStop, ShuttleTimetable
from scripts.route import get_route_list
from scripts.route_stop import get_route_stop_list
from scripts.timetable import insert_shuttle_timetable
from utils.database import get_db_engine


class TestInsertShuttleData:
    connection: Engine | None = None
    session_constructor = None
    session: Session | None = None

    @classmethod
    def setup_class(cls):
        cls.connection = get_db_engine()
        cls.session_constructor = sessionmaker(bind=cls.connection)
        # Database session check
        cls.session = cls.session_constructor()
        assert cls.session is not None
        # Migration schema check
        BaseModel.metadata.create_all(cls.connection)

    @pytest.mark.asyncio
    async def test_insert_shuttle_data(self):
        connection = get_db_engine()
        session_constructor = sessionmaker(bind=connection)
        # Database session check
        session = session_constructor()
        session.execute(delete(ShuttleTimetable))
        session.execute(delete(ShuttleRouteStop))
        session.execute(delete(ShuttleRoute))
        # Insert shuttle route
        await get_route_list(session)
        # Check if the data is inserted
        shuttle_route_count = session.query(ShuttleRoute).count()
        assert shuttle_route_count > 0
        for route_item in session.query(ShuttleRoute).all():  # type: ShuttleRoute
            assert isinstance(route_item.route_name, str)
            assert isinstance(route_item.route_description_korean, str)
            assert isinstance(route_item.route_description_english, str)

        # Insert shuttle route-stop
        await get_route_stop_list(session)
        # Check if the data is inserted
        shuttle_stop_route_count = session.query(ShuttleRouteStop).count()
        assert shuttle_stop_route_count > 0
        for stop_route_item in session.query(ShuttleRouteStop).all():  # type: ShuttleRouteStop
            assert isinstance(stop_route_item.route_name, str)
            assert isinstance(stop_route_item.stop_name, str)
            assert isinstance(stop_route_item.stop_order, int)
            assert isinstance(stop_route_item.cumulative_time, int)

        # Insert shuttle timetable
        await insert_shuttle_timetable(session)
        # Check if the data is inserted
        for timetable_item in session.query(ShuttleTimetable).all():  # type: ShuttleTimetable
            assert isinstance(timetable_item.route_name, str)
            assert isinstance(timetable_item.period_type, str)
            assert isinstance(timetable_item.weekday, bool)
            assert isinstance(timetable_item.departure_time, datetime.time)

        session.close()

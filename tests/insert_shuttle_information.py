import json
from datetime import datetime, timezone, timedelta

from aiohttp import ClientSession
from sqlalchemy import PrimaryKeyConstraint, String
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session, Mapped, mapped_column

from models import BaseModel


class ShuttlePeriodType(BaseModel):
    __tablename__ = "shuttle_period_type"
    period_type: Mapped[str] = mapped_column(String(20), nullable=False, primary_key=True)


class ShuttlePeriod(BaseModel):
    __tablename__ = "shuttle_period"
    __table_args__ = (PrimaryKeyConstraint("period_type", "period_start"),)
    period_type: Mapped[str] = mapped_column(String(20), nullable=False)
    period_start: Mapped[datetime] = mapped_column(nullable=False)
    period_end: Mapped[datetime] = mapped_column(nullable=False)


class ShuttleHoliday(BaseModel):
    __tablename__ = "shuttle_holiday"
    __table_args__ = (PrimaryKeyConstraint("holiday_date", "calendar_type"),)
    holiday_date: Mapped[datetime.date] = mapped_column(nullable=False)
    holiday_type: Mapped[str] = mapped_column(String(15), nullable=False)
    calendar_type: Mapped[str] = mapped_column(String(15), nullable=False)


class ShuttleRoute(BaseModel):
    __tablename__ = "shuttle_route"
    route_id: Mapped[int] = mapped_column(nullable=False, primary_key=True)
    route_name: Mapped[str] = mapped_column(String(15), nullable=False)
    route_description_korean: Mapped[str] = mapped_column(String(100), nullable=False)
    route_description_english: Mapped[str] = mapped_column(String(100), nullable=False)


class ShuttleStop(BaseModel):
    __tablename__ = "shuttle_stop"
    stop_name: Mapped[str] = mapped_column(String(15), nullable=False, primary_key=True)
    latitude: Mapped[float] = mapped_column(nullable=False)
    longitude: Mapped[float] = mapped_column(nullable=False)


async def initialize_subway_data(db_session: Session):
    await insert_shuttle_period_type(db_session)
    await insert_shuttle_period(db_session)
    await insert_shuttle_stop(db_session)


async def insert_shuttle_period_type(db_session: Session):
    period_type_list = [
        dict(period_type="semester"),
        dict(period_type="vacation"),
        dict(period_type="vacation_session"),
    ]
    insert_statement = insert(ShuttlePeriodType).values(period_type_list)
    insert_statement = insert_statement.on_conflict_do_nothing()
    db_session.execute(insert_statement)
    db_session.commit()


async def insert_shuttle_period(db_session: Session):
    url = "https://raw.githubusercontent.com/hyuabot-developers/hyuabot-shuttle-timetable/main/date.json"

    period_items = []
    holiday_items = []
    now = datetime.now(tz=timezone(timedelta(hours=9)))
    async with ClientSession() as session:
        async with session.get(url) as response:
            date_json = json.loads(await response.text())
            for holiday in date_json['holiday']:
                month, day = holiday.split('/')
                if now.month > int(month) or (now.month == int(month) and now.day > int(day)):
                    year = now.year + 1
                else:
                    year = now.year
                holiday_items.append(
                    dict(
                        holiday_type="weekends",
                        holiday_date=datetime.fromisoformat(
                            f"{year}-{str(month).zfill(2)}-{str(day).zfill(2)}"),
                        calendar_type="solar",
                    ))
            for calendar_type, holiday_list in date_json['halt'].items():
                for holiday in holiday_list:
                    month, day = holiday.split('/')
                    if calendar_type == "lunar":
                        year = now.year
                    else:
                        if now.month > int(month) or (now.month == int(month) and now.day > int(day)):
                            year = now.year + 1
                        else:
                            year = now.year
                    holiday_items.append(
                        dict(
                            holiday_type="halt",
                            holiday_date=datetime.fromisoformat(
                                f"{year}-{str(month).zfill(2)}-{str(day).zfill(2)}"),
                            calendar_type=calendar_type,
                        ))
            for period in ["semester", "vacation", "vacation_session"]:
                for period_item in date_json[period]:
                    start_date = datetime.strptime(period_item['start'], "%m/%d") \
                        .replace(year=now.year, hour=0, minute=0, second=0)
                    end_date = datetime.strptime(period_item['end'], "%m/%d") \
                        .replace(year=now.year, hour=23, minute=59, second=59)
                    start_date = datetime.fromisoformat(
                        f"{year}-{str(start_date.month).zfill(2)}-{str(start_date.day).zfill(2)}T00:00:00")
                    end_date = datetime.fromisoformat(
                        f"{year}-{str(end_date.month).zfill(2)}-{str(end_date.day).zfill(2)}T23:59:59")
                    if start_date < end_date:
                        if now.month > int(end_date.month) or \
                                (now.month == int(end_date.month) and now.day > int(end_date.day)):
                            start_date = start_date.replace(year=now.year + 1)
                            end_date = end_date.replace(year=now.year + 1)
                    else:
                        if now.month < int(end_date.month) or \
                                (now.month == int(end_date.month) and now.day < int(end_date.day)):
                            start_date = start_date.replace(year=now.year - 1)
                        else:
                            end_date = end_date.replace(year=now.year + 1)
                    period_items.append(
                        dict(
                            period_type=period,
                            period_start=start_date,
                            period_end=end_date,
                        ))
            db_session.query(ShuttleHoliday).delete()
            db_session.execute(insert(ShuttleHoliday).values(holiday_items))
            db_session.query(ShuttlePeriod).delete()
            db_session.execute(insert(ShuttlePeriod).values(period_items))
            db_session.commit()


async def insert_shuttle_stop(db_session: Session):
    stop_list = [
        dict(stop_name="dormitory_o", latitude=37.29339607529377, longitude=126.83630604103446),
        dict(stop_name="shuttlecock_o", latitude=37.29875417910844, longitude=126.83784054072336),
        dict(stop_name="station", latitude=37.308494476826155, longitude=126.85310236423418),
        dict(stop_name="terminal", latitude=37.31945164682341, longitude=126.8455453372041),
        dict(stop_name="shuttlecock_i", latitude=37.2995897, longitude=126.8372216),
        dict(stop_name="dormitory_i", latitude=37.29339607529377, longitude=126.83630604103446),
        dict(stop_name="jungang_stn", latitude=37.3147818, longitude=126.8397399),
    ]
    insert_statement = insert(ShuttleStop).values(stop_list)
    insert_statement = insert_statement.on_conflict_do_update(
        index_elements=["stop_name"],
        set_=dict(
            latitude=insert_statement.excluded.latitude, longitude=insert_statement.excluded.longitude),
    )
    db_session.execute(insert_statement)
    db_session.commit()

import datetime

from sqlalchemy import PrimaryKeyConstraint, ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class BaseModel(DeclarativeBase):
    pass


class ShuttleRoute(BaseModel):
    __tablename__ = 'shuttle_route'
    route_name: Mapped[str] = mapped_column(String(10), primary_key=True)
    route_tag: Mapped[str] = mapped_column(String(10))
    start_stop: Mapped[str] = mapped_column(String(15))
    end_stop: Mapped[str] = mapped_column(String(15))
    route_description_korean: Mapped[str] = mapped_column(String(100))
    route_description_english: Mapped[str] = mapped_column(String(100))


class ShuttleRouteStop(BaseModel):
    __tablename__ = 'shuttle_route_stop'
    route_name: Mapped[str] = mapped_column(String(10), primary_key=True)
    stop_name: Mapped[str] = mapped_column(String(15), primary_key=True)
    stop_order: Mapped[int] = mapped_column(Integer, primary_key=True)
    cumulative_time: Mapped[int] = mapped_column(Integer)


class ShuttleTimetable(BaseModel):
    __tablename__ = 'shuttle_timetable'
    route_name: Mapped[str] = mapped_column(String(15), primary_key=True)
    stop_name: Mapped[str] = mapped_column(String(15), primary_key=True)
    period_type: Mapped[str] = mapped_column(String(20), primary_key=True)
    weekday: Mapped[bool] = mapped_column(Boolean, primary_key=True)
    departure_time: Mapped[datetime.time] = mapped_column(primary_key=True)

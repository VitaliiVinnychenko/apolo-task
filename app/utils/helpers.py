from datetime import datetime

from fastapi.routing import APIRoute

from app.config import get_settings

settings = get_settings()


def custom_generate_unique_id(route: APIRoute) -> str:
    try:
        return f"{route.tags[0]}-{route.name}"
    except IndexError:
        return route.name


def datetimes_intersection(t1_start: datetime, t1_end: datetime, t2_start: datetime, t2_end: datetime) -> bool:
    return (t1_start <= t2_start < t1_end) or (t2_start <= t1_start < t2_end)

from fastapi.routing import APIRoute

from app.config import get_settings

settings = get_settings()


def custom_generate_unique_id(route: APIRoute) -> str:
    try:
        return f"{route.tags[0]}-{route.name}"
    except IndexError:
        return route.name

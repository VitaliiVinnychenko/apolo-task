import asyncio
from contextlib import ExitStack

import pytest
from app.config import get_settings
from app.main import app as actual_app
from fastapi.testclient import TestClient

settings = get_settings()


@pytest.fixture(autouse=True)
def app():
    with ExitStack():
        yield actual_app


@pytest.fixture
def client(app):
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="session")
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

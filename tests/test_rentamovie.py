import asyncio
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from tortoise.contrib.test import finalizer, initializer

from rentamovie import app
from rentamovie.models import UserCreate


@pytest.fixture(scope="module")
def client() -> Generator:
    initializer(["rentamovie.models"])
    with TestClient(app) as test_client:
        yield test_client
    finalizer()


def test_version(client):
    breakpoint()
    assert client.get("/").status_code == 200

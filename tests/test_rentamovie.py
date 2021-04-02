# pylint: disable=redefined-outer-name
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from tortoise.contrib.test import finalizer, initializer

from rentamovie import app
from rentamovie import models


@pytest.fixture(scope="module")
def client() -> Generator:
    initializer(["rentamovie.models"])
    with TestClient(app) as test_client:
        yield test_client
    finalizer()


@pytest.fixture(scope="module")
def event_loop(client: TestClient) -> Generator:
    yield client.task.get_loop()


SAMPLE_MOVIES = (
    (1, "The Hitchhiker's Guide To The Galaxy", 2005, "comedy"),
    (2, "Halloween", 1978, "horror"),
    (3, "Assassin's Creed", 2016, "action"),
)


async def create_movies():
    for pk, title, year, genre in SAMPLE_MOVIES:
        await models.Movie.create(id=pk, title=title, year=year, genre=genre)


def test_list_movies(client, event_loop):
    event_loop.run_until_complete(create_movies())

    response = client.get("/movies")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": pk,
            "title": title,
            "year": year,
            "genre": genre,
        }
        for pk, title, year, genre in SAMPLE_MOVIES
    ]

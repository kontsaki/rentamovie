# pylint: disable=redefined-outer-name invalid-name
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from tortoise.contrib.test import finalizer, initializer

from rentamovie import app, models, serializers
from rentamovie.main import fastapi_users

TEST_USER_EMAIL = "testuser@email.gr"
TEST_USER_PASSWORD = "123321"


@pytest.fixture()
def client() -> Generator:
    initializer(["rentamovie.models"])
    with TestClient(app) as test_client:
        loop = test_client.task.get_loop()
        loop.run_until_complete(
            fastapi_users.create_user(
                serializers.UserCreate(
                    email=TEST_USER_EMAIL,
                    password=TEST_USER_PASSWORD,
                )
            )
        )
        response = test_client.post(
            "/auth/jwt/login",
            data={"username": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD},
        )
        assert response.status_code == 200
        test_client.headers.update(
            {"Authorization": f"Bearer {response.json()['access_token']}"}
        )
        yield test_client
    finalizer()


@pytest.fixture()
def event_loop(client: TestClient) -> Generator:
    yield client.task.get_loop()


SAMPLE_MOVIES = (
    ("The Hitchhiker's Guide To The Galaxy", 2005, "comedy"),
    ("Halloween", 1978, "horror"),
    ("Assassin's Creed", 2016, "action"),
)


async def create_movies():
    for pk, (title, year, genre) in enumerate(SAMPLE_MOVIES, start=1):
        await models.Movie.create(id=pk, title=title, year=year, genre=genre)


def test_list_movies(client, event_loop):
    event_loop.run_until_complete(create_movies())

    response = client.get("/movies")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": pk,
            "title": title,
        }
        for pk, (title, *_) in enumerate(SAMPLE_MOVIES, start=1)
    ]


def test_movie_details(client, event_loop):
    event_loop.run_until_complete(create_movies())
    movie_id = 1

    response = client.get(f"/movies/{movie_id}")

    assert response.status_code == 200

    title, year, genre = SAMPLE_MOVIES[movie_id - 1]
    assert response.json() == {
        "id": movie_id,
        "title": title,
        "year": year,
        "genre": genre,
    }


def test_rent_movie(client, event_loop):
    event_loop.run_until_complete(create_movies())
    sample_movies = enumerate(SAMPLE_MOVIES, start=1)

    movie_id, (title, year, genre) = next(sample_movies)
    movie = {"id": movie_id, "title": title, "year": year, "genre": genre}

    response = client.post("/movies/rent/", json=movie)

    assert response.status_code == 200, response.json()

    assert response.json() == movie

    response = client.get("/me/movies/")

    assert response.status_code == 200
    assert response.json() == [{"id": movie["id"], "title": movie["title"]}]

    # rent one more
    movie_id, (title, year, genre) = next(sample_movies)
    new_movie = {"id": movie_id, "title": title, "year": year, "genre": genre}

    response = client.post("/movies/rent/", json=new_movie)

    assert response.status_code == 200

    assert response.json() == {
        "id": movie_id,
        "title": title,
        "year": year,
        "genre": genre,
    }

    response = client.get("/me/movies/")

    assert response.status_code == 200
    assert response.json() == [
        {"id": movie["id"], "title": movie["title"]},
        {"id": new_movie["id"], "title": new_movie["title"]},
    ]

# pylint: disable=redefined-outer-name invalid-name
from typing import Generator
from datetime import date, timedelta

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
            "/login",
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
    ("Kung Fu Hustle", 2005, "action"),
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
            "year": year,
            "genre": genre,
        }
        for pk, (title, year, genre) in enumerate(SAMPLE_MOVIES, start=1)
    ]


def test_list_movies_filter_by_year(client, event_loop):
    event_loop.run_until_complete(create_movies())

    response = client.get("/movies?year=2005")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": pk,
            "title": title,
            "year": year,
            "genre": genre,
        }
        for pk, (title, year, genre) in enumerate(SAMPLE_MOVIES, start=1)
        if year == 2005
    ]


def test_list_movies_filter_by_year_and_genre(client, event_loop):
    event_loop.run_until_complete(create_movies())

    response = client.get("/movies?year=2005&genre=action")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": pk,
            "title": title,
            "year": year,
            "genre": genre,
        }
        for pk, (title, year, genre) in enumerate(SAMPLE_MOVIES, start=1)
        if year == 2005 and genre == "action"
    ]


def test_movie_details(client, event_loop):
    event_loop.run_until_complete(create_movies())

    response = client.get("/movies/1")

    assert response.status_code == 200
    title, year, genre = SAMPLE_MOVIES[0]
    assert response.json() == {
        "id": 1,
        "title": title,
        "year": year,
        "genre": genre,
    }


def test_rent_movie(client, event_loop):
    event_loop.run_until_complete(create_movies())
    sample_movies = enumerate(SAMPLE_MOVIES, start=1)

    movie_id, (title, year, genre) = next(sample_movies)
    movie = {"id": movie_id, "title": title, "year": year, "genre": genre}

    response = client.post("/movies/rent", json={"id": movie["id"]})

    assert response.status_code == 200, response.json()
    assert response.json() == movie

    response = client.get("/users/me/movies")

    assert response.status_code == 200
    assert response.json() == [{"id": movie["id"], "title": movie["title"]}]

    # rent one more
    movie_id, (title, year, genre) = next(sample_movies)
    new_movie = {"id": movie_id, "title": title, "year": year, "genre": genre}

    response = client.post("/movies/rent", json={"id": new_movie["id"]})

    assert response.status_code == 200
    assert response.json() == {
        "id": movie_id,
        "title": title,
        "year": year,
        "genre": genre,
    }

    response = client.get("/users/me/movies")

    assert response.status_code == 200
    assert response.json() == [
        {"id": movie["id"], "title": movie["title"]},
        {"id": new_movie["id"], "title": new_movie["title"]},
    ]


def test_cannot_rent_same_movie_twice(client, event_loop):
    event_loop.run_until_complete(create_movies())
    assert client.post("/movies/rent", json={"id": 1}).status_code == 200

    response = client.post("/movies/rent", json={"id": 1})

    assert response.status_code == 400
    assert response.json()["detail"] == "Cannot rent same movie twice."


def test_rent_non_existing_movie(client, event_loop):
    event_loop.run_until_complete(create_movies())

    response = client.post("/movies/rent", json={"id": len(SAMPLE_MOVIES) + 100})

    assert response.status_code == 400
    assert response.json()["detail"] == "Movie does not exist."


def test_get_user_balance(client):
    response = client.get("/users/me")

    assert response.status_code == 200
    print(response.json())
    assert response.json()["balance"] == 0


def test_return_movie(client, event_loop):
    event_loop.run_until_complete(create_movies())
    title, year, genre = SAMPLE_MOVIES[0]
    assert client.post("/movies/rent", json={"id": 1}).status_code == 200
    assert client.get("/users/me/movies").json() == [{"id": 1, "title": title}]

    response = client.post("/movies/return", json={"id": 1})

    assert response.status_code == 200, response.headers
    assert response.json() == {
        "id": 1,
        "title": title,
        "year": year,
        "genre": genre,
    }

    assert client.get("/users/me/movies").json() == []
    assert client.get("/users/me").json()["balance"] == -1.0


def test_cannot_return_same_movie_twice_or_not_rented_movie(client, event_loop):
    event_loop.run_until_complete(create_movies())
    assert client.post("/movies/rent", json={"id": 1}).status_code == 200
    assert client.post("/movies/return", json={"id": 1}).status_code == 200

    response = client.post("/movies/return", json={"id": 1})

    assert response.status_code == 400
    assert response.json()["detail"] == "This movie was not rented."


async def create_rent(movie_id, days):
    user = await models.User.get(email=TEST_USER_EMAIL)
    movie = await models.Movie.get(id=movie_id)
    past = date.today() - timedelta(days=days)
    await models.Rent.create(user=user, movie=movie, date=past)


@pytest.mark.parametrize(
    "days, cost",
    [
        (1, 1.0),
        (2, 2.0),
        (3, 3.0),
        (4, 3.5),
        (5, 4.0),
        (6, 4.5),
    ],
)
def test_return_movie_cost_per_day(days, cost, client, event_loop):
    event_loop.run_until_complete(create_movies())
    event_loop.run_until_complete(create_rent(movie_id=1, days=days))

    response = client.post("/movies/return", json={"id": 1})

    assert response.status_code == 200, response.headers
    assert client.get("/users/me").json()["balance"] == -cost

    assert client.get(f"/movies/cost/{days}").text == str(cost)


@pytest.mark.parametrize(
    "method, url",
    [("get", "/users/me/movies"), ("post", "/movies/rent"), ("post", "/movies/return")],
)
def test_endpoints_with_mandatory_authentication(method, url):
    with TestClient(app) as client:
        assert getattr(client, method)(url).status_code == 401

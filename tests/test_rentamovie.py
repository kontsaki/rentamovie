from rentamovie import app
from fastapi.testing import TestClient


client = TestClient(app)


def test_version():
    assert client.get("/").status_code == 200

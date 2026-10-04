import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from extensions import db
from config import Config


class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    TESTING = True


@pytest.fixture()
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


def register_and_login(client, name, email, password, role):
    client.post("/api/auth/register", json={
        "name": name, "email": email, "password": password, "role": role,
    })
    resp = client.post("/api/auth/login", json={"email": email, "password": password})
    return resp.get_json()["access_token"]


@pytest.fixture()
def tourist_token(client):
    return register_and_login(client, "Turista Test", "turista@test.com", "clave123", "turista")


@pytest.fixture()
def host_token(client):
    return register_and_login(client, "Anfitrion Test", "anfitrion@test.com", "clave123", "anfitrion")


@pytest.fixture()
def admin_token(client):
    return register_and_login(client, "Admin Test", "admin@test.com", "clave123", "administrador")


@pytest.fixture()
def sample_listing(client, host_token):
    resp = client.post(
        "/api/listings",
        json={"title": "Cabaña de prueba", "city": "Medellín", "price_per_night": 100000},
        headers={"Authorization": f"Bearer {host_token}"},
    )
    return resp.get_json()

"""
Suite de pruebas del backend StayDragon.
Ejecutar con:  pytest -v   (desde la carpeta backend/)
"""
from unittest.mock import patch


# ---------------------------------------------------------------------------
# Autenticación (RF-01)
# ---------------------------------------------------------------------------
def test_register_creates_user_and_returns_token(client):
    resp = client.post("/api/auth/register", json={
        "name": "Ana", "email": "ana@test.com", "password": "secreta123", "role": "turista",
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["user"]["email"] == "ana@test.com"
    assert "access_token" in data


def test_register_duplicate_email_fails(client):
    client.post("/api/auth/register", json={
        "name": "Ana", "email": "ana@test.com", "password": "secreta123", "role": "turista",
    })
    resp = client.post("/api/auth/register", json={
        "name": "Ana 2", "email": "ana@test.com", "password": "otra123", "role": "turista",
    })
    assert resp.status_code == 409


def test_login_wrong_password_fails(client):
    client.post("/api/auth/register", json={
        "name": "Ana", "email": "ana@test.com", "password": "secreta123", "role": "turista",
    })
    resp = client.post("/api/auth/login", json={"email": "ana@test.com", "password": "incorrecta"})
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Publicaciones (RF-03, RF-04, RF-05)
# ---------------------------------------------------------------------------
def test_tourist_cannot_create_listing(client, tourist_token):
    resp = client.post(
        "/api/listings",
        json={"title": "No debería crearse", "city": "Cali", "price_per_night": 50000},
        headers={"Authorization": f"Bearer {tourist_token}"},
    )
    assert resp.status_code == 403


def test_host_can_create_listing(client, host_token):
    resp = client.post(
        "/api/listings",
        json={"title": "Finca de prueba", "city": "Rionegro", "price_per_night": 150000},
        headers={"Authorization": f"Bearer {host_token}"},
    )
    assert resp.status_code == 201
    assert resp.get_json()["title"] == "Finca de prueba"


def test_search_filters_by_city(client, sample_listing):
    resp = client.get("/api/listings?city=Medellin")
    assert resp.status_code == 200
    resp_match = client.get("/api/listings?city=Medellín")
    assert len(resp_match.get_json()) == 1

    resp_no_match = client.get("/api/listings?city=Bogota")
    assert resp_no_match.get_json() == []


def test_listing_detail_includes_reviews_field(client, sample_listing):
    resp = client.get(f"/api/listings/{sample_listing['id']}")
    assert resp.status_code == 200
    assert "reviews" in resp.get_json()


# ---------------------------------------------------------------------------
# Reservas y pagos (RF-06, RF-07, RF-08)
# ---------------------------------------------------------------------------
def test_create_booking_success_and_payment_approved(client, tourist_token, sample_listing):
    resp = client.post(
        "/api/bookings",
        json={
            "listing_id": sample_listing["id"],
            "check_in": "2026-11-10",
            "check_out": "2026-11-12",
            "guests": 2,
            "payment_method": "tarjeta",
        },
        headers={"Authorization": f"Bearer {tourist_token}"},
    )
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["status"] == "confirmada"
    assert data["total_price"] == 200000  # 2 noches x 100000
    assert data["payment"]["status"] == "aprobado"


def test_overlapping_booking_is_rejected(client, tourist_token, sample_listing):
    client.post(
        "/api/bookings",
        json={"listing_id": sample_listing["id"], "check_in": "2026-12-01", "check_out": "2026-12-05",
              "guests": 1, "payment_method": "tarjeta"},
        headers={"Authorization": f"Bearer {tourist_token}"},
    )
    resp = client.post(
        "/api/bookings",
        json={"listing_id": sample_listing["id"], "check_in": "2026-12-03", "check_out": "2026-12-06",
              "guests": 1, "payment_method": "tarjeta"},
        headers={"Authorization": f"Bearer {tourist_token}"},
    )
    assert resp.status_code == 409


def test_host_can_block_date_and_booking_on_it_is_rejected(client, host_token, tourist_token, sample_listing):
    client.post(
        f"/api/listings/{sample_listing['id']}/blocked-dates",
        json={"date": "2026-12-25"},
        headers={"Authorization": f"Bearer {host_token}"},
    )
    resp = client.post(
        "/api/bookings",
        json={"listing_id": sample_listing["id"], "check_in": "2026-12-24", "check_out": "2026-12-26",
              "guests": 1, "payment_method": "tarjeta"},
        headers={"Authorization": f"Bearer {tourist_token}"},
    )
    assert resp.status_code == 409


def test_checkout_before_checkin_is_rejected(client, tourist_token, sample_listing):
    resp = client.post(
        "/api/bookings",
        json={"listing_id": sample_listing["id"], "check_in": "2026-12-10", "check_out": "2026-12-05",
              "guests": 1, "payment_method": "tarjeta"},
        headers={"Authorization": f"Bearer {tourist_token}"},
    )
    assert resp.status_code == 400


# ---------------------------------------------------------------------------
# Reseñas (RF-09)
# ---------------------------------------------------------------------------
def test_review_requires_confirmed_booking(client, tourist_token, sample_listing):
    resp = client.post(
        "/api/reviews",
        json={"listing_id": sample_listing["id"], "rating": 5, "comment": "Sin reserva previa"},
        headers={"Authorization": f"Bearer {tourist_token}"},
    )
    assert resp.status_code == 403


def test_review_allowed_after_confirmed_booking(client, tourist_token, sample_listing):
    client.post(
        "/api/bookings",
        json={"listing_id": sample_listing["id"], "check_in": "2026-11-10", "check_out": "2026-11-12",
              "guests": 1, "payment_method": "tarjeta"},
        headers={"Authorization": f"Bearer {tourist_token}"},
    )
    resp = client.post(
        "/api/reviews",
        json={"listing_id": sample_listing["id"], "rating": 4, "comment": "Muy buena experiencia"},
        headers={"Authorization": f"Bearer {tourist_token}"},
    )
    assert resp.status_code == 201


# ---------------------------------------------------------------------------
# Panel administrativo (RF-13)
# ---------------------------------------------------------------------------
def test_non_admin_cannot_access_admin_stats(client, tourist_token):
    resp = client.get("/api/admin/stats", headers={"Authorization": f"Bearer {tourist_token}"})
    assert resp.status_code == 403


def test_admin_can_access_stats(client, admin_token, sample_listing):
    resp = client.get("/api/admin/stats", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    assert resp.get_json()["total_publicaciones"] >= 1


# ---------------------------------------------------------------------------
# Geolocalización (RF-10) - se simula la respuesta de Nominatim para no
# depender de una llamada de red real durante las pruebas automatizadas.
# ---------------------------------------------------------------------------
def test_geo_search_returns_parsed_coordinates(client):
    fake_nominatim_response = [
        {"display_name": "Rionegro, Antioquia, Colombia", "lat": "6.1537", "lon": "-75.3738"}
    ]

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return fake_nominatim_response

    with patch("routes.geo_routes.requests.get", return_value=FakeResponse()):
        resp = client.get("/api/geo/search?q=Rionegro")

    assert resp.status_code == 200
    data = resp.get_json()
    assert data[0]["latitude"] == 6.1537
    assert data[0]["longitude"] == -75.3738


def test_geo_search_requires_query_param(client):
    resp = client.get("/api/geo/search")
    assert resp.status_code == 400

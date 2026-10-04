"""
Prueba estructural ("smoke test") de la app Flet.

No reemplaza probar la app real con `python main.py` (eso hay que grabarlo
en el video, porque abre una ventana nativa), pero sí deja evidencia
automatizada de que cada pantalla se construye sin errores, usando un
ApiClient simulado (sin red) y una Page falsa (sin interfaz gráfica).

Uso:  python smoke_test.py
"""
import sys
import flet as ft

from views import (
    login_view, register_view, home_view, detail_view,
    booking_view, my_bookings_view, host_panel_view, admin_view,
)


class FakePage:
    def __init__(self):
        self.controls = []
        self.snack_bar = None

    def update(self):
        pass


class FakeApi:
    """Sustituye al ApiClient real devolviendo datos de muestra, sin red."""
    def __init__(self, role="turista"):
        self.token = "fake-token"
        self.user = {"id": 1, "name": "Usuario Demo", "email": "demo@test.com", "role": role}

    def search_listings(self, **kw):
        return [{
            "id": 1, "title": "Finca Demo", "city": "Rionegro", "country": "Colombia",
            "category": "alojamiento", "price_per_night": 180000, "average_rating": 4.8,
            "review_count": 3,
        }]

    def get_listing(self, listing_id):
        return {
            "id": listing_id, "title": "Finca Demo", "city": "Rionegro", "country": "Colombia",
            "description": "Descripción de prueba", "price_per_night": 180000,
            "average_rating": 4.8, "review_count": 1, "host_name": "María Gómez",
            "reviews": [{"rating": 5, "author": "Juan", "comment": "Excelente"}],
        }

    def my_listings(self):
        return [{"title": "Finca Demo", "city": "Rionegro", "price_per_night": 180000, "is_active": True}]

    def host_bookings(self):
        return [{"id": 1, "check_in": "2026-11-01", "check_out": "2026-11-03", "status": "confirmada", "total_price": 360000}]

    def my_bookings(self):
        return [{
            "id": 1, "status": "confirmada", "check_in": "2026-11-01", "check_out": "2026-11-03",
            "nights": 2, "guests": 2, "total_price": 360000,
            "payment": {"status": "aprobado", "transaction_id": "TXN-DEMO"},
        }]

    def admin_stats(self):
        return {"total_usuarios": 3, "total_turistas": 1, "total_anfitriones": 1,
                "total_publicaciones": 2, "total_reservas": 1, "reservas_confirmadas": 1}

    def admin_users(self):
        return [{"id": 1, "name": "Admin", "email": "admin@staydragon.co", "role": "administrador"}]

    def geocode(self, q):
        return [{"display_name": q, "latitude": 6.25, "longitude": -75.56}]

    def logout(self):
        self.token = None


def check(name, fn):
    try:
        page = FakePage()
        control = fn(page)
        assert isinstance(control, ft.Control), f"{name} no devolvió un control válido"
        print(f"[OK] {name}")
        return True
    except Exception as exc:
        print(f"[FALLA] {name}: {exc}")
        return False


def noop_navigate(*a, **kw):
    pass


def main():
    results = []
    api_turista = FakeApi("turista")
    api_anfitrion = FakeApi("anfitrion")
    api_admin = FakeApi("administrador")
    state = {"selected_listing": {"id": 1, "title": "Finca Demo", "price_per_night": 180000}}

    results.append(check("login_view", lambda p: login_view.build(p, api_turista, noop_navigate)))
    results.append(check("register_view", lambda p: register_view.build(p, api_turista, noop_navigate)))
    results.append(check("home_view", lambda p: home_view.build(p, api_turista, noop_navigate, {})))
    results.append(check("detail_view", lambda p: detail_view.build(p, api_turista, noop_navigate, {}, 1)))
    results.append(check("booking_view", lambda p: booking_view.build(p, api_turista, noop_navigate, state)))
    results.append(check("my_bookings_view", lambda p: my_bookings_view.build(p, api_turista, noop_navigate, {})))
    results.append(check("host_panel_view", lambda p: host_panel_view.build(p, api_anfitrion, noop_navigate, {})))
    results.append(check("admin_view", lambda p: admin_view.build(p, api_admin, noop_navigate, {})))

    total = len(results)
    passed = sum(results)
    print(f"\n{passed}/{total} pantallas construidas correctamente")
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()

"""
StayDragon - App móvil (Flet)
Punto de entrada. Para ejecutar:

    cd mobile_app
    python main.py

Requiere que el backend (../backend) esté corriendo en http://127.0.0.1:5000
"""
import flet as ft
from api_client import ApiClient
from views import (
    login_view, register_view, home_view, detail_view,
    booking_view, my_bookings_view, host_panel_view, admin_view,
)

VIEW_BUILDERS = {
    "login": lambda page, api, navigate, state, **kw: login_view.build(page, api, navigate),
    "register": lambda page, api, navigate, state, **kw: register_view.build(page, api, navigate),
    "home": lambda page, api, navigate, state, **kw: home_view.build(page, api, navigate, state),
    "detail": lambda page, api, navigate, state, **kw: detail_view.build(page, api, navigate, state, kw.get("listing_id")),
    "booking": lambda page, api, navigate, state, **kw: booking_view.build(page, api, navigate, state),
    "my_bookings": lambda page, api, navigate, state, **kw: my_bookings_view.build(page, api, navigate, state),
    "host_panel": lambda page, api, navigate, state, **kw: host_panel_view.build(page, api, navigate, state),
    "admin": lambda page, api, navigate, state, **kw: admin_view.build(page, api, navigate, state),
}


def main(page: ft.Page):
    page.title = "StayDragon"
    page.window.width = 420
    page.window.height = 860
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.bgcolor = "white"

    api = ApiClient()
    state = {}

    def navigate(view_name, **kwargs):
        builder = VIEW_BUILDERS.get(view_name)
        if builder is None:
            raise ValueError(f"Vista desconocida: {view_name}")
        page.controls.clear()
        content = builder(page, api, navigate, state, **kwargs)
        if content is not None:
            page.controls.append(content)
        page.update()

    navigate("login")


if __name__ == "__main__":
    ft.app(target=main)

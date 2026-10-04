import flet as ft
from api_client import ApiError
from components import top_bar, show_error, primary_button, GREEN


def build(page, api, navigate):
    email = ft.TextField(label="Correo electrónico", autofocus=True)
    password = ft.TextField(label="Contraseña", password=True, can_reveal_password=True)

    def do_login(e):
        if not email.value or not password.value:
            show_error(page, "Completa correo y contraseña")
            return
        try:
            api.login(email.value.strip(), password.value)
        except ApiError as ex:
            show_error(page, str(ex))
            return
        role = api.user["role"]
        if role == "turista":
            navigate("home")
        elif role == "anfitrion":
            navigate("host_panel")
        else:
            navigate("admin")

    return ft.Column(
        expand=True,
        controls=[
            top_bar(page, "StayDragon", api, navigate, show_logout=False),
            ft.Container(
                padding=24,
                content=ft.Column([
                    ft.Text("Bienvenido a StayDragon", size=20, weight=ft.FontWeight.BOLD, color=GREEN),
                    ft.Text("Turismo rural y experiencias auténticas", size=13, color="#666"),
                    ft.Container(height=16),
                    email,
                    password,
                    ft.Container(height=8),
                    primary_button("Iniciar sesión", do_login),
                    ft.Container(height=8),
                    ft.TextButton("¿No tienes cuenta? Regístrate", on_click=lambda e: navigate("register")),
                    ft.Container(height=20),
                    ft.Text("Usuarios de prueba (ver seed.py):", size=11, color="#999"),
                    ft.Text("turista: juan@staydragon.co / turista123", size=11, color="#999"),
                    ft.Text("anfitrión: maria@staydragon.co / anfitrion123", size=11, color="#999"),
                    ft.Text("admin: admin@staydragon.co / admin123", size=11, color="#999"),
                ]),
            ),
        ],
    )

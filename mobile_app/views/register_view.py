import flet as ft
from api_client import ApiError
from components import top_bar, show_error, primary_button, GREEN


def build(page, api, navigate):
    name = ft.TextField(label="Nombre completo", autofocus=True)
    email = ft.TextField(label="Correo electrónico")
    password = ft.TextField(label="Contraseña", password=True, can_reveal_password=True)
    role = ft.Dropdown(
        label="Quiero registrarme como",
        value="turista",
        options=[
            ft.dropdown.Option("turista", "Turista"),
            ft.dropdown.Option("anfitrion", "Anfitrión"),
        ],
    )

    def do_register(e):
        if not all([name.value, email.value, password.value]):
            show_error(page, "Completa todos los campos")
            return
        try:
            api.register(name.value.strip(), email.value.strip(), password.value, role.value)
        except ApiError as ex:
            show_error(page, str(ex))
            return
        navigate("home" if role.value == "turista" else "host_panel")

    return ft.Column(
        expand=True,
        controls=[
            top_bar(page, "Crear cuenta", api, navigate, show_logout=False),
            ft.Container(
                padding=24,
                content=ft.Column([
                    name, email, password, role,
                    ft.Container(height=8),
                    primary_button("Registrarme", do_register),
                    ft.TextButton("Ya tengo cuenta, iniciar sesión", on_click=lambda e: navigate("login")),
                ]),
            ),
        ],
    )

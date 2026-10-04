import flet as ft
from api_client import ApiError
from components import top_bar, show_error, GREEN


def build(page, api, navigate, state):
    try:
        bookings = api.my_bookings()
    except ApiError as ex:
        show_error(page, str(ex))
        bookings = []

    rows = []
    if not bookings:
        rows.append(ft.Text("Todavía no tienes reservas.", color="#777"))
    for b in bookings:
        rows.append(
            ft.Container(
                padding=12,
                border=ft.border.all(1, "#d8d8d8"),
                border_radius=10,
                content=ft.Column([
                    ft.Text(f"Reserva #{b['id']} — {b['status'].upper()}", weight=ft.FontWeight.BOLD, color=GREEN),
                    ft.Text(f"{b['check_in']} → {b['check_out']}  ({b['nights']} noches, {b['guests']} huéspedes)"),
                    ft.Text(f"Total: ${b['total_price']:,.0f}"),
                    ft.Text(
                        f"Pago: {b['payment']['status']} · {b['payment']['transaction_id']}"
                        if b.get("payment") else "Sin pago registrado",
                        size=12, color="#666",
                    ),
                ]),
            )
        )

    return ft.Column(
        expand=True,
        scroll=ft.ScrollMode.AUTO,
        controls=[
            top_bar(page, "Mis reservas", api, navigate),
            ft.Container(padding=16, content=ft.Column([
                ft.TextButton("← Volver a buscar", on_click=lambda e: navigate("home")),
                *rows,
            ])),
        ],
    )

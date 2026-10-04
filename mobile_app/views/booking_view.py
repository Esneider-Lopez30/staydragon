import flet as ft
from api_client import ApiError
from components import top_bar, show_error, show_success, primary_button, GREEN


def build(page, api, navigate, state):
    listing = state.get("selected_listing")
    if not listing:
        navigate("home")
        return ft.Column([ft.Text("Selecciona primero una experiencia.")])

    check_in = ft.TextField(label="Fecha de entrada (YYYY-MM-DD)", value="2026-11-10")
    check_out = ft.TextField(label="Fecha de salida (YYYY-MM-DD)", value="2026-11-12")
    guests = ft.TextField(label="Huéspedes", value="2", width=120)
    method = ft.RadioGroup(
        value="tarjeta",
        content=ft.Column([
            ft.Radio(value="tarjeta", label="Tarjeta de crédito / débito"),
            ft.Radio(value="pse", label="PSE / transferencia"),
            ft.Radio(value="billetera", label="Billetera digital (Nequi/Daviplata)"),
        ]),
    )
    result_text = ft.Text("", color=GREEN, weight=ft.FontWeight.BOLD)

    def confirm_payment(e):
        try:
            g = int(guests.value or 1)
        except ValueError:
            show_error(page, "Huéspedes debe ser un número")
            return
        try:
            booking = api.create_booking(
                listing["id"], check_in.value.strip(), check_out.value.strip(), g, method.value
            )
        except ApiError as ex:
            show_error(page, str(ex))
            return

        txn = booking["payment"]["transaction_id"]
        total = booking["total_price"]
        result_text.value = (
            f"¡Reserva confirmada! Total pagado: ${total:,.0f}. "
            f"Transacción: {txn}"
        )
        show_success(page, "Pago aprobado y reserva confirmada")
        page.update()

    return ft.Column(
        expand=True,
        scroll=ft.ScrollMode.AUTO,
        controls=[
            top_bar(page, "Confirmar y pagar", api, navigate),
            ft.Container(
                padding=16,
                content=ft.Column([
                    ft.Text(listing["title"], weight=ft.FontWeight.BOLD, size=16),
                    ft.Text(f"${listing['price_per_night']:,.0f} / noche", color="#666"),
                    ft.Divider(),
                    check_in,
                    check_out,
                    guests,
                    ft.Container(height=10),
                    ft.Text("Método de pago", weight=ft.FontWeight.BOLD, color=GREEN),
                    method,
                    ft.Container(height=10),
                    primary_button("Pagar y confirmar reserva", confirm_payment),
                    ft.Container(height=10),
                    result_text,
                    ft.TextButton("Ver mis reservas", on_click=lambda e: navigate("my_bookings")),
                ]),
            ),
        ],
    )

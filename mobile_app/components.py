import flet as ft

GREEN = "#2E5339"
GREEN_LIGHT = "#DCEFE0"
GOLD = "#8A6D3B"


def top_bar(page, title, api, navigate, show_logout=True):
    actions = []
    if show_logout and api.user:
        actions.append(
            ft.IconButton(
                icon=ft.Icons.LOGOUT,
                tooltip="Cerrar sesión",
                icon_color="white",
                on_click=lambda e: (api.logout(), navigate("login")),
            )
        )
    return ft.Container(
        bgcolor=GREEN,
        padding=ft.padding.symmetric(vertical=16, horizontal=16),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Text(title, color="white", size=18, weight=ft.FontWeight.BOLD),
                ft.Row(actions),
            ],
        ),
    )


def show_error(page, message):
    page.open(ft.SnackBar(ft.Text(message), bgcolor="#C0392B"))


def show_success(page, message):
    page.open(ft.SnackBar(ft.Text(message), bgcolor=GREEN))


def primary_button(text, on_click):
    return ft.ElevatedButton(
        text=text,
        on_click=on_click,
        bgcolor=GREEN,
        color="white",
        height=46,
    )


def listing_card(listing, on_view):
    rating = listing.get("average_rating")
    rating_text = f"{rating} ★ ({listing.get('review_count', 0)})" if rating else "Sin calificaciones aún"
    return ft.Container(
        padding=12,
        border=ft.border.all(1, "#d8d8d8"),
        border_radius=10,
        content=ft.Column([
            ft.Text(listing["title"], weight=ft.FontWeight.BOLD, size=15),
            ft.Text(f"{listing['city']}, {listing['country']}  ·  {listing['category']}", size=12, color="#666"),
            ft.Text(rating_text, size=12, color="#666"),
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text(f"${listing['price_per_night']:,.0f} / noche", weight=ft.FontWeight.BOLD, color=GREEN),
                    ft.TextButton("Ver detalle", on_click=lambda e: on_view(listing["id"])),
                ],
            ),
        ]),
    )

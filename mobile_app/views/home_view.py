import flet as ft
from api_client import ApiError
from components import top_bar, show_error, listing_card, GREEN


def build(page, api, navigate, state):
    city_field = ft.TextField(label="Ciudad o destino", expand=True)
    category_dd = ft.Dropdown(
        label="Categoría",
        width=160,
        value="",
        options=[
            ft.dropdown.Option("", "Todas"),
            ft.dropdown.Option("alojamiento", "Alojamiento"),
            ft.dropdown.Option("actividad", "Actividad"),
        ],
    )
    results_column = ft.Column(spacing=10)

    def view_listing(listing_id):
        navigate("detail", listing_id=listing_id)

    def run_search(e=None):
        try:
            listings = api.search_listings(city=city_field.value or "", category=category_dd.value or "")
        except ApiError as ex:
            show_error(page, str(ex))
            return
        results_column.controls.clear()
        if not listings:
            results_column.controls.append(ft.Text("No se encontraron experiencias con esos filtros.", color="#777"))
        for listing in listings:
            results_column.controls.append(listing_card(listing, view_listing))
        page.update()

    # carga inicial
    run_search()

    return ft.Column(
        expand=True,
        scroll=ft.ScrollMode.AUTO,
        controls=[
            top_bar(page, "Buscar experiencias", api, navigate),
            ft.Container(
                padding=16,
                content=ft.Column([
                    ft.Row([city_field, category_dd]),
                    ft.ElevatedButton("Buscar", on_click=run_search, bgcolor=GREEN, color="white"),
                    ft.Divider(),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text("Resultados", weight=ft.FontWeight.BOLD),
                            ft.TextButton("Mis reservas", on_click=lambda e: navigate("my_bookings")),
                        ],
                    ),
                    results_column,
                ]),
            ),
        ],
    )

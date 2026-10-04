import flet as ft
from api_client import ApiError
from components import top_bar, show_error, show_success, primary_button, GREEN


def build(page, api, navigate, state):
    # ---------- formulario de nueva publicación ----------
    title = ft.TextField(label="Título de la experiencia")
    description = ft.TextField(label="Descripción", multiline=True, min_lines=2, max_lines=4)
    category = ft.Dropdown(
        label="Categoría", value="alojamiento",
        options=[ft.dropdown.Option("alojamiento", "Alojamiento"), ft.dropdown.Option("actividad", "Actividad")],
    )
    city = ft.TextField(label="Ciudad")
    price = ft.TextField(label="Precio por noche (COP)", value="150000")
    geo_status = ft.Text("", size=12, color="#666")
    lat_holder = {"lat": None, "lon": None}

    def buscar_coordenadas(e):
        print("CLICK GEO", flush=True)
        if not city.value:
            show_error(page, "Escribe primero una ciudad para geolocalizar")
            return
        try:
            results = api.geocode(f"{city.value}, Colombia")
        except ApiError as ex:
            show_error(page, str(ex))
            return
        if not results:
            geo_status.value = "No se encontraron coordenadas para esa ciudad."
        else:
            lat_holder["lat"] = results[0]["latitude"]
            lat_holder["lon"] = results[0]["longitude"]
            geo_status.value = f"📍 {results[0]['display_name']} ({lat_holder['lat']:.4f}, {lat_holder['lon']:.4f})"
        page.update()
        try:
            geo_status.update()
        except Exception:
            pass

    listings_column = ft.Column(spacing=8)

    def refresh_listings():
        try:
            mine = api.my_listings()
        except ApiError as ex:
            show_error(page, str(ex))
            return
        listings_column.controls.clear()
        if not mine:
            listings_column.controls.append(ft.Text("Aún no tienes publicaciones.", color="#777"))
        for l in mine:
            listings_column.controls.append(
                ft.Container(
                    padding=10, border=ft.border.all(1, "#d8d8d8"), border_radius=8,
                    content=ft.Column([
                        ft.Text(l["title"], weight=ft.FontWeight.BOLD),
                        ft.Text(f"{l['city']} · ${l['price_per_night']:,.0f}/noche · {'activa' if l['is_active'] else 'inactiva'}", size=12, color="#666"),
                    ]),
                )
            )
        page.update()
        try:
            listings_column.update()
        except Exception:
            pass

    def publicar(e):
        print("CLICK PUBLICAR", flush=True)
        if not title.value or not city.value or not price.value:
            show_error(page, "Título, ciudad y precio son obligatorios")
            return
        try:
            api.create_listing({
                "title": title.value, "description": description.value, "category": category.value,
                "city": city.value, "price_per_night": float(price.value),
                "latitude": lat_holder["lat"], "longitude": lat_holder["lon"],
            })
        except (ApiError, ValueError) as ex:
            show_error(page, str(ex))
            return
        show_success(page, "Publicación creada")
        title.value, description.value, city.value = "", "", ""
        geo_status.value = ""
        refresh_listings()

    # ---------- reservas recibidas ----------
    bookings_column = ft.Column(spacing=8)

    def load_bookings(e=None):
        try:
            received = api.host_bookings()
        except ApiError as ex:
            show_error(page, str(ex))
            return
        bookings_column.controls.clear()
        if not received:
            bookings_column.controls.append(ft.Text("Aún no has recibido reservas.", color="#777"))
        for b in received:
            bookings_column.controls.append(
                ft.Text(f"Reserva #{b['id']} · {b['check_in']} → {b['check_out']} · {b['status']} · ${b['total_price']:,.0f}")
            )
        page.update()
        try:
            bookings_column.update()
        except Exception:
            pass

    refresh_listings()
    load_bookings()

    tabs = ft.Tabs(
        selected_index=0,
        tabs=[
            ft.Tab(text="Publicar", content=ft.Container(padding=12, content=ft.Column(
                scroll=ft.ScrollMode.AUTO,
                controls=[
                    title, description, category, city,
                    ft.Row([price, ft.TextButton("Buscar coordenadas", on_click=buscar_coordenadas)]),
                    geo_status,
                    primary_button("Publicar experiencia", publicar),
                ],
            ))),
            ft.Tab(text="Mis publicaciones", content=ft.Container(padding=12, content=ft.Column(
                scroll=ft.ScrollMode.AUTO, controls=[listings_column],
            ))),
            ft.Tab(text="Reservas recibidas", content=ft.Container(padding=12, content=ft.Column(
                scroll=ft.ScrollMode.AUTO,
                controls=[
                    ft.ElevatedButton("Actualizar", on_click=load_bookings),
                    bookings_column,
                ],
            ))),
        ],
        expand=True,
    )

    return ft.Column(
        expand=True,
        controls=[
            top_bar(page, "Panel del anfitrión", api, navigate),
            tabs,
        ],
    )
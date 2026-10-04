import flet as ft
from api_client import ApiError
from components import top_bar, show_error, primary_button, GREEN


def build(page, api, navigate, state, listing_id):
    try:
        listing = api.get_listing(listing_id)
    except ApiError as ex:
        show_error(page, str(ex))
        listing = None

    if not listing:
        return ft.Column([top_bar(page, "Detalle", api, navigate), ft.Text("No se pudo cargar la publicación.")])

    rating = listing.get("average_rating")
    rating_text = f"{rating} ★ ({listing.get('review_count', 0)} reseñas)" if rating else "Sin calificaciones aún"

    reviews_controls = [ft.Text("Reseñas", weight=ft.FontWeight.BOLD, color=GREEN)]
    if listing.get("reviews"):
        for r in listing["reviews"]:
            reviews_controls.append(ft.Text(f"⭐ {r['rating']} — {r['author']}: {r['comment']}", size=12))
    else:
        reviews_controls.append(ft.Text("Todavía no hay reseñas para esta experiencia.", size=12, color="#777"))

    def go_booking(e):
        state["selected_listing_id"] = listing["id"]
        state["selected_listing"] = listing
        navigate("booking")

    return ft.Column(
        expand=True,
        scroll=ft.ScrollMode.AUTO,
        controls=[
            top_bar(page, "Detalle", api, navigate),
            ft.Container(
                padding=16,
                content=ft.Column([
                    ft.Text(listing["title"], size=20, weight=ft.FontWeight.BOLD),
                    ft.Text(f"{listing['city']}, {listing['country']}  ·  {rating_text}", color="#666"),
                    ft.Divider(),
                    ft.Text("Descripción", weight=ft.FontWeight.BOLD, color=GREEN),
                    ft.Text(listing.get("description") or "Sin descripción."),
                    ft.Container(height=10),
                    ft.Text(f"Anfitrión: {listing.get('host_name', 'N/D')}", size=12, color="#666"),
                    ft.Container(height=10),
                    *reviews_controls,
                    ft.Container(height=20),
                    primary_button(f"Reservar ahora — ${listing['price_per_night']:,.0f}/noche", go_booking),
                ]),
            ),
        ],
    )

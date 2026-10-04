import flet as ft
from api_client import ApiError
from components import top_bar, show_error, GREEN


def _stat_card(label, value):
    return ft.Container(
        padding=14, border=ft.border.all(1, "#d8d8d8"), border_radius=10, expand=True,
        content=ft.Column([
            ft.Text(str(value), size=22, weight=ft.FontWeight.BOLD, color=GREEN),
            ft.Text(label, size=11, color="#666"),
        ]),
    )


def build(page, api, navigate, state):
    try:
        stats = api.admin_stats()
        users = api.admin_users()
    except ApiError as ex:
        show_error(page, str(ex))
        stats, users = {}, []

    stat_row1 = ft.Row([
        _stat_card("Usuarios", stats.get("total_usuarios", 0)),
        _stat_card("Turistas", stats.get("total_turistas", 0)),
        _stat_card("Anfitriones", stats.get("total_anfitriones", 0)),
    ])
    stat_row2 = ft.Row([
        _stat_card("Publicaciones", stats.get("total_publicaciones", 0)),
        _stat_card("Reservas", stats.get("total_reservas", 0)),
        _stat_card("Confirmadas", stats.get("reservas_confirmadas", 0)),
    ])

    user_rows = [
        ft.DataRow(cells=[
            ft.DataCell(ft.Text(str(u["id"]))),
            ft.DataCell(ft.Text(u["name"])),
            ft.DataCell(ft.Text(u["email"])),
            ft.DataCell(ft.Text(u["role"])),
        ])
        for u in users
    ]

    table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Nombre")),
            ft.DataColumn(ft.Text("Correo")),
            ft.DataColumn(ft.Text("Rol")),
        ],
        rows=user_rows,
    )

    return ft.Column(
        expand=True,
        scroll=ft.ScrollMode.AUTO,
        controls=[
            top_bar(page, "Panel administrativo", api, navigate),
            ft.Container(padding=16, content=ft.Column([
                ft.Text("Reportes generales (RF-13)", weight=ft.FontWeight.BOLD, color=GREEN),
                stat_row1,
                stat_row2,
                ft.Divider(),
                ft.Text("Gestión de usuarios", weight=ft.FontWeight.BOLD, color=GREEN),
                ft.Row([table], scroll=ft.ScrollMode.AUTO),
            ])),
        ],
    )

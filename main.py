import flet as ft
from pages.camera import camera_page
from pages.history import history_page
from pages.vehicles import vehicles_page
from pages.users import users_page

def main(page: ft.Page):
    page.title = "Vehicle Tracker"
    content = ft.Column(expand=True)
    content.controls.append(vehicles_page(page))
    def on_navigation(e):
        content.controls.clear()
        if e.control.selected_index == 0:
            content.controls.append(camera_page(page))
        elif e.control.selected_index == 1:
            content.controls.append(vehicles_page(page))
        elif e.control.selected_index == 2:
            content.controls.append(history_page(page))
        elif e.control.selected_index == 3:
            content.controls.append(users_page(page))
        page.update()

    rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        # extended=True,
        min_width=100,
        leading = ft.Text("Vehicle Tracker", size=20),
        min_extended_width=400,
        group_alignment=-0.9,
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.icons.CAMERA_OUTLINED,
                selected_icon_content=ft.Icon(ft.icons.CAMERA),
                label_content=ft.Text("Camera"),
            ),
            ft.NavigationRailDestination(
                icon=ft.icons.DIRECTIONS_CAR,
                selected_icon_content=ft.Icon(ft.icons.DIRECTIONS_CAR),
                label_content=ft.Text("Vehículos"),
            ),
            ft.NavigationRailDestination(
                icon=ft.icons.WORK_HISTORY,
                selected_icon_content=ft.Icon(ft.icons.WORK_HISTORY),
                label_content=ft.Text("Historial"),
            ),
            ft.NavigationRailDestination(
                icon=ft.icons.PERSON,
                selected_icon_content=ft.Icon(ft.icons.PERSON),
                label_content=ft.Text("Usuarios"),
            )
        ],
        on_change=lambda e: on_navigation(e),
    )
    page.add(
        ft.Row(
            [
                rail,
                ft.VerticalDivider(width=1),
                content
            ],
            expand=True,
        )
    )

ft.app(main)

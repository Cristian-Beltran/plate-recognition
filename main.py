import flet as ft
from pages.camera import camera_page,stop_camera
from pages.history import history_page
from pages.vehicles import vehicles_page
from pages.users import users_page
from services.user_service import UserService

user_service = UserService()
def login_page(page: ft.Page, on_login_success):

    page.update()
    def login_click(e):
        login = user_service.login(username.value, password.value)
        if login:
            on_login_success(login.role)  # Si el login es correcto, llama a la función de éxito
        else:
            error_message.value = "Usuario o contraseña incorrectos"
            error_message.update()


    username = ft.TextField(label="Usuario", width=300)
    password = ft.TextField(label="Contraseña", password=True, width=300)
    error_message = ft.Text(value="", color=ft.colors.RED)
    # Estructura del formulario de login
    page.add(
        ft.Container(
            content=ft.Column(
                [
                    ft.Text("Iniciar sesión", size=30, weight=ft.FontWeight.BOLD),
                    username,
                    password,
                    error_message,
                    ft.ElevatedButton("Ingresar", on_click=login_click),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            alignment=ft.alignment.center,
            expand=True
        )
    )
    users = user_service.get_users()
    if(len(users) == 0):
        user_service.create_user("admin", "admin", "admin","Administrador")

def main(page: ft.Page):
    page.title = "Vehicle Tracker"
    page.window_width = 400
    page.window_height = 350
    page.window.resizable = False
    def show_main_content(rol):
        page.window_width = 1100
        page.window_height = 700
        page.window.resizable = True
        page.update()
        content = ft.Column(expand=True)
        content.controls.append(camera_page(page))
        def on_navigation(e):
            stop_camera()
            content.controls.clear()
            if e.control.selected_index == 0:
                content.controls.append(camera_page(page))
            elif e.control.selected_index == 1:
                content.controls.append(history_page(page))
            elif e.control.selected_index == 2:
                content.controls.append(users_page(page))
            elif e.control.selected_index == 3:
                content.controls.append(vehicles_page(page))
            page.update()
        if rol == "Administrador":
            destinations = [
                ft.NavigationRailDestination(
                    icon=ft.icons.CAMERA_OUTLINED,
                    selected_icon_content=ft.Icon(ft.icons.CAMERA),
                    label_content=ft.Text("Camera"),
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
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.DIRECTIONS_CAR,
                    selected_icon_content=ft.Icon(ft.icons.DIRECTIONS_CAR),
                    label_content=ft.Text("Vehículos"),
                ),
            ]
        else:
            destinations = [
                ft.NavigationRailDestination(
                    icon=ft.icons.CAMERA_OUTLINED,
                    selected_icon_content=ft.Icon(ft.icons.CAMERA),
                    label_content=ft.Text("Camera"),
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.WORK_HISTORY,
                    selected_icon_content=ft.Icon(ft.icons.WORK_HISTORY),
                    label_content=ft.Text("Historial"),
                ),
            ]
        rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            # extended=True,
            min_width=100,
            leading = ft.Text("Vehicle Tracker", size=20),
            min_extended_width=400,
            group_alignment=-0.9,
            destinations=destinations,
            on_change=lambda e: on_navigation(e),
        )
        page.controls.clear()
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
    login_page(page, show_main_content)

ft.app(main)

import flet as ft
import os
from pages.camera import camera_page,stop_camera
from pages.history import history_page
from pages.vehicles import vehicles_page
from pages.users import users_page
from services.user_service import UserService

import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

user_service = UserService()
def send_password_reset_email(email,code):
    sender = "cristian.beltran.paco@gmail.com"
    receiver = email
    password = "fgzyngdpxvuobaqz"
    # Crear el mensaje
    message = MIMEMultipart()
    message["From"] = sender
    message["To"] = receiver
    message["Subject"] = "Restablecer contraseña"
    # Cuerpo del correo (texto simple)
    body = f"Codigo:{code} "
    message.attach(MIMEText(body, "plain"))
    try:
        # Conectar al servidor SMTP de Gmail
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.sendmail(sender, receiver, message.as_string())
            print(f"Correo enviado con éxito a {receiver} con el código {code}")
    except Exception as e:
        print(f"Error al enviar el correo: {e}")


def login_page(page: ft.Page, on_login_success):
    page.update()
    def login_click(e):
        login = user_service.login(username.value, password.value)
        if login:
            user_service.add_last_login(login.id)
            on_login_success(login.role,f"{login.first_name} {login.last_name}")  # Si el login es correcto, llama a la función de éxito
        else:
            error_message.value = "Usuario o contraseña incorrectos"
            error_message.update()

    def reset_password_click(e):
        code = ""
        email = ""

        def send_code_email(e):
            global code
            global email
            code = str(random.randint(1000, 9999))
            email = emailText.value
            if not user_service.get_user_email(email):
                error_message_reset.value = "Email no existe"
                page.update()
                return
            send_password_reset_email(email,code)
            send_message.value = "Se ha enviado un código a tu email"

        emailText = ft.TextField(label="Email", width=300)
        button = ft.ElevatedButton("Enviar Codigo", on_click=send_code_email)
        code_input = ft.TextField(label="Codigo", width=300)
        passwor_input = ft.TextField(label="Contraseña", password=True, width=300)
        password_confirm = ft.TextField(label="Confirmar contraseña", password=True, width=300)
        error_message_reset = ft.Text("",color=ft.colors.RED_400)
        send_message = ft.Text("", color=ft.colors.GREEN_400)
        def reset(e):
            global code
            global email
            print(email, code, passwor_input.value, password_confirm.value)
            if (email == "" and code == ""):
                error_message_reset.value = "Email o código no ingresados"
                page.update()
                return

            if(passwor_input.value == password_confirm.value and code_input.value == code):
                user_service.reset_password(email,passwor_input.value)
                user = user_service.get_user_email(email)
                handle_close(e)
                on_login_success(user.role,f"{user.first_name} {user.last_name}")
            else:
                error_message_reset.value = "Contraseñas no coinciden"
                page.update()

        def handle_close(e):
            page.close(modal)

        modal = ft.AlertDialog(
            modal=True,
            title=ft.Text("Resetear contraseña"),
            content=ft.Column([
                error_message_reset,
                emailText,
                button,
                send_message,
                code_input,
                passwor_input,
                password_confirm,
            ]),
            actions=[
                ft.TextButton("Resetear", on_click=reset),
                ft.TextButton("Cerrar", on_click=handle_close),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.open(modal)

    username = ft.TextField(label="Usuario", width=300)
    password = ft.TextField(label="Contraseña", password=True, width=300)
    error_message = ft.Text(value="", color=ft.colors.RED)
    logo = os.path.abspath('assets/logo.png')
    # Estructura del formulario de login
    page.add(
        ft.Container(
            content=ft.Column(
                [
                    ft.Card(
                        content=ft.Container(
                        content=ft.Column([
                            ft.Text("Bienvenido", size=40, weight=ft.FontWeight.BOLD),
                            # Imagen centrada de logo
                            ft.Container(
                                content=ft.Image(src=logo, width=200, height=100, fit=ft.ImageFit.CONTAIN, repeat=ft.ImageRepeat.NO_REPEAT),
                                alignment=ft.alignment.center,
                                border_radius=8,
                            ),
                            ft.Divider(),
                            ft.Text("Iniciar sesión", size=30, weight=ft.FontWeight.BOLD),
                            username,
                            password,
                            error_message,
                            ft.ElevatedButton("Ingresar", on_click=login_click),
                            ft.TextButton("Olvidé mi contraseña", on_click=reset_password_click),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ), width=400, padding=20)
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            alignment=ft.alignment.center,
            expand=True,
        )
    )
    users = user_service.get_users()
    if(len(users) == 0):
        user_service.create_user("admin@gmail.com","admin","admin","sistema","0000","00000","Administrador")

def main(page: ft.Page):
    page.title = "Vehicle Tracker"
    page.dark_theme = ft.Theme(
            color_scheme=ft.ColorScheme(
                primary=ft.colors.CYAN,
                on_primary=ft.colors.BLACK,
                primary_container=ft.colors.CYAN_700,
                on_primary_container=ft.colors.WHITE,
                secondary=ft.colors.LIME,
                on_secondary=ft.colors.BLACK,
                secondary_container=ft.colors.LIME_700,
                on_secondary_container=ft.colors.WHITE,
                error=ft.colors.RED_ACCENT,
                on_error=ft.colors.BLACK,
                background=ft.colors.BLACK,
                on_background=ft.colors.WHITE,
                surface=ft.colors.GREY_900,
                on_surface=ft.colors.WHITE,
            )
        )
    page.theme_mode = ft.ThemeMode.DARK
    page.window.resizable = False
    def logout(page):
        stop_camera()
        page.controls.clear()
        login_page(page, show_main_content)

    def show_main_content(rol,full_name):
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
            leading = ft.Column([ft.Row([ft.Text("Vehicle Tracker", size=20), ft.IconButton(ft.icons.LOGOUT, on_click=lambda e: logout(page))]), ft.Text(full_name, size=10, color=ft.colors.GREY_500)]),
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

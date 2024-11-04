import flet as ft
import shutil
from services.user_service import UserService
import os
import base64
import openpyxl
from openpyxl import Workbook
import re

user_service = UserService()
rows = []

email = ft.TextField(label="Email", expand=True)
password = ft.TextField(label="Contraseña", password=True, can_reveal_password=True,expand=True)
first_name = ft.TextField(label="Nombre",expand=True)
last_name = ft.TextField(label="Apellido",expand=True)
ci = ft.TextField(label="CI",expand=True)
cellphone = ft.TextField(label="Celular",expand=True)
role = ft.Dropdown(label="Rol", options=[ft.dropdown.Option("Administrador"), ft.dropdown.Option("Operador")],expand=True)
default_image = os.path.abspath('assets/icon.png')
image = ft.Image(src=default_image, width=100, height=100)
# get image assets icon.png
repeat_password = ft.TextField(label="Repetir contraseña", password=True, can_reveal_password=True,expand=True)
user_global_id = None


folder_name = "user_images"
if not os.path.exists(folder_name):
    os.makedirs(folder_name)

selected_image_path = None

def users_page(page: ft.Page):
    def encode_image_to_base64(image_path):
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        return encoded_string
    global user_global_id
    def upload_image(e):
        global selected_image_path
        selected_image_path = e.files[0].path
        if selected_image_path:
            # Mostrar la imagen en la app
            image.src_base64 = encode_image_to_base64(selected_image_path)
            page.update()
    upload_file_dialog = ft.FilePicker(on_result=upload_image)

    def handle_route_change(r: ft.RouteChangeEvent):
        if page.route == "/update":
            page.views.append(
                ft.View(
                    route="/update",
                    fullscreen_dialog=True,     # MAIN parameter for the full-screen dialog!
                    appbar=ft.AppBar(title=ft.Text("Editar Usuario"),),
                    controls=[update_user_modal()],
                )
            )
            page.update()
        if page.route == "/add":
            page.views.append(
                ft.View(
                    route="/add",
                    fullscreen_dialog=True,     # MAIN parameter for the full-screen dialog!
                    appbar=ft.AppBar(title=ft.Text("Crear Usuario"),),
                    controls=[add_user_modal()],
                )
            )
            page.update()


    def handle_view_pop(view: ft.ViewPopEvent):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    def download_data(path):
        wb = Workbook()
        ws = wb.active
        if ws is None:
            ws = wb.create_sheet()
        ws.title = "Usuarios"
        ws.append(["Id", "Email", "CI", "Rol", "Celular", "Ultimo ingreso", "Creado"])
        name = "Usuarios"
        rows = [entry for entry in user_service.get_users()]
        for entry in rows:
            ws.append([str(entry.id), entry.email, entry.ci, entry.role, entry.cellphone, formate_date(entry.last_login), formate_date(entry.created_at)])
        full_path = os.path.join(path, name + ".xlsx")
        wb.save(full_path)

    def get_directory_result(path):
        download_data(path.path)

    def on_add_user_click(e: ft.ControlEvent):
        image.src_base64 = encode_image_to_base64(default_image)
        selected_image_path=None
        page.go("/add")
        page.update()

    def update_user(user_id):
        clear_form()
        global user_global_id
        user_global_id = user_id
        user = user_service.get_user(user_global_id)
        email.value = user.email
        first_name.value = user.first_name
        last_name.value = user.last_name
        ci.value = user.ci
        cellphone.value = user.cellphone
        password.value = user.password
        role.value = user.role
        image.src_base64 = encode_image_to_base64(default_image)
        selected_image_path=None
        file = os.path.join(folder_name, f"{user_global_id}.jpg")
        if os.path.exists(file):
            image.src_base64 = encode_image_to_base64(file)
        page.update()
        page.go("/update")

    def formate_date(date):
        if(date == None):
            return ""
        return date.strftime("%d/%m/%Y")
    def delete_user(user_id):
        user_service.delete_user(user_id)
        get_users()
        page.dialog.open = False
        page.update()

    def delete_user_modal(user_id):
        def close_modal(e):
            page.dialog.open = False
            page.update()
        modal = ft.AlertDialog(
            title=ft.Text("Eliminar Usuario"),
            content=ft.Text("¿Está seguro de eliminar este usuario?"),
            actions = [ft.ElevatedButton("Eliminar ", on_click=lambda e, user_id=user_id: delete_user(user_id)), ft.TextButton("Cancelar", on_click=lambda e: close_modal(e))]
        )
        page.dialog = modal
        modal.open = True
        page.update()

    def get_users():
        rows.clear()
        users = user_service.get_users()
        for user in users:
            image_user = ft.Image(src_base64=encode_image_to_base64(default_image), width=50, height=50, fit=ft.ImageFit.COVER)
            image_icon = os.path.join(folder_name, f"{user.id}.jpg")
            if os.path.exists(image_icon):
                image_user.src_base64 = encode_image_to_base64(image_icon)
            rows.append(ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(str(user.id))),
                    ft.DataCell(
                        ft.Row([
                            image_user,
                            ft.Column([
                                ft.Text(f"{user.first_name} {user.last_name}"),
                                ft.Text(user.email, style=ft.TextThemeStyle.BODY_SMALL, color=ft.colors.GREY_500)
                            ], horizontal_alignment=ft.CrossAxisAlignment.START, alignment=ft.MainAxisAlignment.CENTER, spacing=2)
                        ])),
                    ft.DataCell(ft.Text(user.ci)),
                    ft.DataCell(ft.Text(user.role)),
                    ft.DataCell(ft.Text(user.cellphone)),
                    ft.DataCell(ft.Text(formate_date(user.last_login))),
                    ft.DataCell(ft.Text(formate_date(user.created_at))),
                    ft.DataCell(ft.Row([
                        ft.IconButton(ft.icons.EDIT, on_click=lambda e, id=user.id: update_user(id)),
                        ft.IconButton(ft.icons.DELETE, on_click=lambda e, id=user.id: delete_user_modal(id)),
                    ]))
                ]
            ))


    def validate_form():
        if not email.value:
            email.error_text = "El email es requerido"
            return False
        else:
            email.error_text = ""
        if not password.value:
            password.error_text = "El campo 'Contraseña' es obligatorio"
            return False
        elif len(password.value) < 8:
            password.error_text = "La contraseña debe tener al menos 8 caracteres"
            return False
        elif not re.search(r"[A-Z]", password.value):
            password.error_text = "La contraseña debe tener al menos una letra mayúscula"
            return False
        elif not re.search(r"\d", password.value):
            password.error_text = "La contraseña debe tener al menos un número"
            return False
        else:
            password.error_text = None

        if not first_name.value:
            password.error_text = "El nombre es requerido"
            return False
        else:
            first_name.error_text = ""
        if not ci.value:
            ci.error_text = "El CI es requerido"
            return False
        else:
            ci.error_text = ""
        if not cellphone.value:
            cellphone.error_text = "El celular es requerido"
            return False
        else:
            cellphone.error_text = ""
        if not role.value:
            role.error_text = "El rol es requerido"
            return False
        else:
            role.error_text = ""
        return True

    def clear_form():
        email.value = ""
        email.error_text = ""
        first_name.value = ""
        first_name.error_text = ""
        last_name.value = ""
        last_name.error_text = ""
        ci.value = ""
        ci.error_text = ""
        cellphone.value = ""
        cellphone.error_text = ""
        password.value = ""
        password.error_text = ""
        role.value = ""
        role.error_text = ""

    def update_user_modal():
        global user_global_id
        if(user_global_id== None):
            return ft.Container()

        def close_modal(e):
            page.views.pop()
            top_view = page.views[-1]
            page.go(top_view.route)

        def add_user(e):
            if(not validate_form()):
                page.update()
                return
            try:
                if(selected_image_path):
                    new_image_name = f"{user_global_id}.jpg"
                    copy = os.path.join(folder_name, new_image_name)
                    shutil.copy(selected_image_path, copy)
            except Exception as error:
                print(f"Error al copiar la imagen: {error}")

            user_service.update_user(user_global_id,email.value, password.value, first_name.value, last_name.value, ci.value, cellphone.value, role.value)
            get_users()
            page.update()
            close_modal(e)


        return ft.Container(
            ft.Column([
                ft.Row([
                    ft.Container(ft.Column([
                        ft.Text("Foto de perfil"),
                        image,
                        ft.ElevatedButton("Subir foto", on_click=lambda _: upload_file_dialog.pick_files( allow_multiple=False))
                    ])),
                    ft.Column([
                        first_name,
                        last_name
                    ],expand=True)
                ]),
                ft.Column([
                    ft.Row([
                        ci,
                        cellphone,
                        role
                    ]),
                    email,
                    ft.Row([
                        password,
                        repeat_password
                    ])
                ]),
                ft.Row([
                    ft.ElevatedButton("Actualizar", on_click=add_user),
                    ft.TextButton("Cerrar", on_click=close_modal)
                ])
            ],horizontal_alignment=ft.CrossAxisAlignment.CENTER, width=500),
            expand=True, alignment=ft.alignment.center
        )
    def add_user_modal():
        clear_form()
        def close_modal(e):
            page.views.pop()
            top_view = page.views[-1]
            page.go(top_view.route)

        def add_user(e):
            if(not validate_form()):
                page.update()
                return
            user_service.create_user(email.value, password.value, first_name.value, last_name.value, ci.value, cellphone.value, role.value)
            user = user_service.get_last_user()
            try:
                if(selected_image_path):
                    new_image_name = f"{user.id}.jpg"
                    copy = os.path.join(folder_name, new_image_name)
                    shutil.copy(selected_image_path, copy)
            except Exception as error:
                print(f"Error al copiar la imagen: {error}")

            get_users()
            page.update()
            close_modal(e)

        return ft.Container(
            ft.Column([
                ft.Row([
                    ft.Container(ft.Column([
                        ft.Text("Foto de perfil"),
                        image,
                        ft.ElevatedButton("Subir foto", on_click=lambda _: upload_file_dialog.pick_files( allow_multiple=False))
                    ])),
                    ft.Column([
                        first_name,
                        last_name
                    ],expand=True)
                ]),
                ft.Column([
                    ft.Row([
                        ci,
                        cellphone,
                        role
                    ]),
                    email,
                    ft.Row([
                        password,
                        repeat_password
                    ])
                ]),
                ft.Row([
                    ft.ElevatedButton("Agregar", on_click=add_user),
                    ft.TextButton("Cerrar", on_click=close_modal)
                ])
            ],horizontal_alignment=ft.CrossAxisAlignment.CENTER, width=500),
            expand=True, alignment=ft.alignment.center
        )



    def on_search_change(event):
        search_term = event.control.value.lower()
        filtered_users = [user for user in user_service.get_users() if search_term in user.first_name.lower()]
        rows.clear()
        for user in filtered_users:
            image_user = ft.Image(src=default_image, width=50, height=50, fit=ft.ImageFit.COVER)
            image_icon = os.path.join(folder_name, f"{user.id}.jpg")
            if os.path.exists(image_icon):
                image_user.src_base64 = encode_image_to_base64(image_icon)
            rows.append(ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(str(user.id))),
                    ft.DataCell(
                        ft.Row([
                            image_user,
                            ft.Column([
                                ft.Text(f"{user.first_name} {user.last_name}"),
                                ft.Text(user.email, style=ft.TextThemeStyle.BODY_SMALL, color=ft.colors.GREY_500)
                            ], horizontal_alignment=ft.CrossAxisAlignment.START, alignment=ft.MainAxisAlignment.CENTER, spacing=2)
                        ])),
                    ft.DataCell(ft.Text(user.ci)),
                    ft.DataCell(ft.Text(user.role)),
                    ft.DataCell(ft.Text(user.cellphone)),
                    ft.DataCell(ft.Text(formate_date(user.last_login))),
                    ft.DataCell(ft.Text(formate_date(user.created_at))),
                    ft.DataCell(ft.Row([
                        ft.IconButton(ft.icons.EDIT, on_click=lambda e, id=user.id: update_user(id)),
                        ft.IconButton(ft.icons.DELETE, on_click=lambda e, id=user.id: delete_user_modal(id)),
                    ]))
                ]
            ))
        page.update()

    title = ft.Text("Registro de usuarios", theme_style=ft.TextThemeStyle.HEADLINE_MEDIUM)
    input_search = ft.TextField(label="Buscar", on_submit=on_search_change, icon=ft.icons.SEARCH)
    add_user = ft.IconButton(icon=ft.icons.ADD,icon_color="blue400", on_click=on_add_user_click,tooltip="Agregar usuario")
    get_directory_dialog = ft.FilePicker(on_result=get_directory_result)
    page.on_route_change = handle_route_change
    page.on_view_pop = handle_view_pop

    page.overlay.extend([upload_file_dialog,get_directory_dialog])
    get_users()
    return ft.Column([
        title,
        ft.Row([input_search, add_user, ft.ElevatedButton("Descargar", icon=ft.icons.DOWNLOAD, on_click=lambda _: get_directory_dialog.get_directory_path())],spacing=20),
        ft.Column([
            ft.Row([
                ft.Stack(
                height = 300,
                controls=[
                    ft.Column([
                        ft.DataTable(
                            column_spacing=20,
                            columns=[
                                ft.DataColumn(ft.Text("Id"), numeric=True),
                                ft.DataColumn(ft.Text("Usuario")),
                                ft.DataColumn(ft.Text("CI")),
                                ft.DataColumn(ft.Text("Rol")),
                                ft.DataColumn(ft.Text("Celular")),
                                ft.DataColumn(ft.Text("Ultimo ingreso")),
                                ft.DataColumn(ft.Text("Crado")),
                                ft.DataColumn(ft.Text("Acciones"))
                            ],
                            rows=rows,
                        )
                    ],scroll=ft.ScrollMode.ALWAYS),
                ])
            ],
            expand=False,
            scroll=ft.ScrollMode.ALWAYS)
        ],expand=1,
        adaptive=True,
        scroll=ft.ScrollMode.ALWAYS)
    ],
    expand=True)

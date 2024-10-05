import flet as ft
from services.user_service import UserService

user_service = UserService()
rows = []

fullname = ft.TextField(label="Nombre completo")
username = ft.TextField(label="Nombre de usuario")
password = ft.TextField(label="Contraseña", password=True, can_reveal_password=True)
role = ft.Dropdown(label="Rol", options=[ft.dropdown.Option("Administrador"), ft.dropdown.Option("Usuario")])

def validate_form():
    if not fullname.value:
        fullname.error_text = "El nombre completo es requerido"
        return False
    else:
        fullname.error_text = ""

    if not username.value:
        username.error_text = "El nombre de usuario es requerido"
        return False
    else:
        username.error_text = ""
    if not password.value:
        password.error_text = "La contraseña es requerida"
        return False
    else:
        password.error_text = ""

    if not role.value:
        role.error_text = "El rol es requerido"
        return False
    else:
        role.error_text = ""
    return True

def clear_form():
    fullname.value = ""
    fullname.error_text = ""
    username.value = ""
    username.error_text = ""
    password.value = ""
    password.error_text = ""
    role.value = ""
    role.error_text = ""

def get_users(page):
    rows.clear()
    users = user_service.get_users()
    for user in users:
        rows.append(ft.DataRow(
            cells=[
                ft.DataCell(ft.Text(str(user.id))),
                ft.DataCell(ft.Text(user.fullname)),
                ft.DataCell(ft.Text(user.username)),
                ft.DataCell(ft.Text(user.role)),
                ft.DataCell(ft.Row([
                    ft.IconButton(ft.icons.EDIT, on_click=lambda e: update_user_modal(page,user.id)),
                    ft.IconButton(ft.icons.DELETE, on_click=lambda e: delete_user_modal(page,user.id))
                ]))
            ]
        ))

def update_user_modal(page,user_id):
    clear_form()
    user = user_service.get_user(user_id)
    username.value = user.username
    password.value = user.password
    fullname.value = user.fullname
    role.value = user.role

    def close_modal(e):
        page.dialog.open = False
        page.update()

    def update_user(user_id):
        if(not validate_form()):
            page.update()
            return
        user_service.update_user(user_id, username=username.value, password=password.value, fullname=fullname.value, role=role.value)
        get_users(page)
        page.dialog.open = False
        page.update()

    modal = ft.AlertDialog(
        title=ft.Text("Editar Usuario"),
        content=ft.Column([
            fullname,
            username,
            password,
            role,
        ]),
        actions=[ft.ElevatedButton("Editar", on_click=lambda e: update_user(user_id)) ,ft.TextButton("Cerrar", on_click=lambda e: close_modal(e))]
    )
    page.dialog = modal
    modal.open = True
    page.update()


def delete_user_modal(page, user_id):
    def close_modal(e):
        page.dialog.open = False
        page.update()
    def delete_user(user_id):
        user_service.delete_user(user_id)
        get_users(page)
        page.dialog.open = False
        page.update()

    modal = ft.AlertDialog(
        title=ft.Text("Eliminar Usuario"),
        content=ft.Text("¿Está seguro de eliminar este usuario?"),
        actions = [ft.ElevatedButton("Eliminar", on_click=lambda e: delete_user), ft.TextButton("Cancelar", on_click=lambda e: close_modal(e))]
    )
    page.dialog = modal
    modal.open = True
    page.update()


def add_user_modal(page):
    clear_form()
    def close_modal(e):
        page.dialog.open = False
        page.update()

    def add_user(e):
        if(not validate_form()):
            page.update()
            return
        user_service.create_user(username.value , password.value, fullname.value, role.value)
        get_users(page)
        page.update()
        close_modal(e)

    modal = ft.AlertDialog(
        title=ft.Text("Agregar Nuevo Usuario"),
        content=ft.Column([
            fullname,
            username,
            password,
            role,
        ]),
        actions=[ft.ElevatedButton("Agregar", on_click=add_user),ft.TextButton("Cerrar", on_click=close_modal)]
    )
    page.dialog = modal
    modal.open = True
    page.update()

def users_page(page: ft.Page):
    def on_search_change(event):
        search_term = event.control.value.lower()
        filtered_users = [user for user in user_service.get_users() if search_term in user.username.lower()]
        rows.clear()
        for user in filtered_users:
            rows.append(ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(str(user.id))),
                    ft.DataCell(ft.Text(user.fullname)),
                    ft.DataCell(ft.Text(user.username)),
                    ft.DataCell(ft.Text(user.role)),
                    ft.DataCell(ft.Row([
                        ft.IconButton(ft.icons.EDIT, on_click=lambda e, id=user.id: update_user_modal(page, id)),
                        ft.IconButton(ft.icons.DELETE, on_click=lambda e, id=user.id: delete_user_modal(page, id))
                    ]))
                ]
            ))
        page.update()

    def on_add_user_click(event):
        add_user_modal(page)

    title = ft.Text("Registro de usuarios", theme_style=ft.TextThemeStyle.HEADLINE_MEDIUM)
    input_search = ft.TextField(label="Buscar", on_submit=on_search_change, icon=ft.icons.SEARCH)
    add_user = ft.IconButton(icon=ft.icons.ADD,icon_color="blue400", on_click=on_add_user_click,tooltip="Agregar usuario")
    get_users(page)
    return ft.Column([
        title,
        ft.Row([input_search, add_user],spacing=20),
        ft.ListView([ft.DataTable(
            width=800,
            columns=[
                ft.DataColumn(ft.Text("Id"), numeric=True),
                ft.DataColumn(ft.Text("Nombre completo")),
                ft.DataColumn(ft.Text("Nombre de usuario")),
                ft.DataColumn(ft.Text("Rol")),
                ft.DataColumn(ft.Text("Acciones"))
            ],
            rows=rows,
            expand=True,
        )],expand=1, spacing=10, padding=20, auto_scroll=True)
    ],
    expand=True
    )

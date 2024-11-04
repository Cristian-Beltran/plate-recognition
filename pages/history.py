import flet as ft
from services.history_service import HistoryService
from datetime import datetime
import openpyxl
from openpyxl import Workbook
import os
import base64

default_image = os.path.abspath('assets/icon.png')
image = ft.Image(src=default_image, width=100, height=100)
def format_date(date):
    return date.strftime("%d/%m/%Y")

def get_hours(date):
    return date.strftime("%H:%M")

folder_name_drivers = "drivers_images"
if not os.path.exists(folder_name_drivers):
    os.makedirs(folder_name_drivers)
history_service = HistoryService()
history_auth = ft.Switch(label="Autorizados", value=True, )
rows = []
date_text = ft.Text("Fecha: "+ format_date(datetime.now()))
date_value = datetime.now().date()
text_value = ""
columns=[
    ft.DataColumn(ft.Text("Id"), numeric=True),
    ft.DataColumn(ft.Text("Placa")),
    ft.DataColumn(ft.Text("Fecha")),
    ft.DataColumn(ft.Text("Hora")),
    ft.DataColumn(ft.Text("Tipo")),
    ft.DataColumn(ft.Text("Conductor")),
    ft.DataColumn(ft.Text("CI")),
    ft.DataColumn(ft.Text("Personal")),
    ft.DataColumn(ft.Text("Marca")),
    ft.DataColumn(ft.Text("Color")),
    ft.DataColumn(ft.Text("Acciones"))
]

size_font=11

input_search = ft.TextField(label="Buscar", icon=ft.icons.SEARCH,expand=True)
personal_filter = ft.Dropdown(label="Personal", value="Todos", options=[ft.dropdown.Option("Todos"), ft.dropdown.Option("Docente"), ft.dropdown.Option("Estudiante")],expand=True)
check_authorized = ft.Checkbox(label="Autorizados", value=True,expand=True)
check_not_authorized = ft.Checkbox(label="No Autorizados", value=False,expand=True)
card = ft.Card(content=ft.Text(""), expand=True)

def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    return encoded_string


def generate_card(data):
    if data.authorized:
        file = os.path.join(folder_name_drivers, f"{data.vehicle.plate}_driver.jpg")
        color = ft.colors.RED_600 if data.type == "Salida" else ft.colors.GREEN_600
        return ft.Container(
            content=ft.Column([
                ft.Container(content=ft.Text(f"{data.plate}", size=30, weight=ft.FontWeight.BOLD,  text_align=ft.TextAlign.CENTER), alignment=ft.alignment.center),

                # Imagen del vehículo
                ft.Container(
                    content=ft.Image(src_base64=data.image, width=200, height=150, fit=ft.ImageFit.CONTAIN, repeat=ft.ImageRepeat.NO_REPEAT),
                    alignment=ft.alignment.center,
                    border_radius=8,
                ),

                # Fecha y Hora en fila con fondo
                ft.Row([
                    ft.Container(
                        content=ft.Text(f"Fecha: {format_date(data.created_at)}", size=size_font),
                        padding=ft.padding.all(8),  # Ajuste aquí
                        bgcolor=ft.colors.GREY_600,
                        border_radius=5,
                    ),
                    ft.Container(
                        content=ft.Text(f"Hora: {get_hours(data.created_at)}", size=size_font),
                        padding=ft.padding.all(8),  # Ajuste aquí
                        bgcolor=ft.colors.GREY_600,
                        border_radius=5,
                    ),
                ], spacing=10, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

                # Información del conductor en fila con fondo
                ft.Row([
                    ft.Container(
                        content=ft.Image(src=file, width=70, fit=ft.ImageFit.CONTAIN, repeat=ft.ImageRepeat.NO_REPEAT),
                        alignment=ft.alignment.center,
                    ),
                    ft.Column([
                        ft.Container(
                            content=ft.Text(f"Marca: {data.vehicle.make}", size=size_font),
                            padding=ft.padding.all(6),  # Ajuste aquí
                            bgcolor=ft.colors.GREY_600,
                            border_radius=5,
                        ),
                        ft.Container(
                            content=ft.Text(f"Color: {data.vehicle.color}", size=size_font),
                            padding=ft.padding.all(6),  # Ajuste aquí
                            bgcolor=ft.colors.GREY_600,
                            border_radius=5,
                        ),
                        ft.Container(
                            content=ft.Text(f"Nombre: {data.vehicle.first_name} {data.vehicle.last_name}", size=size_font),
                            padding=ft.padding.all(6),  # Ajuste aquí
                            bgcolor=ft.colors.GREY_600,
                            border_radius=5,
                        ),
                    ], spacing=4)
                ]),

                # Personal, CI y tipo en fila
                ft.Row([
                    ft.Container(
                        content=ft.Text(f"Personal: {data.vehicle.personal}", size=size_font),
                        padding=ft.padding.all(8),  # Ajuste aquí
                        bgcolor=ft.colors.GREY_600,
                        border_radius=5,
                    ),
                    ft.Container(
                        content=ft.Text(f"CI: {data.vehicle.ci}", size=size_font),
                        padding=ft.padding.all(8),  # Ajuste aquí
                        bgcolor=ft.colors.GREY_600,
                        border_radius=5,
                    ),
                    ft.Container(
                        content=ft.Text(f"{data.type}", size=size_font, color=ft.colors.WHITE),
                        padding=ft.padding.all(8),  # Ajuste aquí
                        bgcolor=color,
                        border_radius=5,
                    ),
                ], spacing=4, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Container(content=ft.Text(f"{data.type}", size=size_font, color=ft.colors.WHITE), padding=ft.padding.all(8), bgcolor=color, border_radius=5, alignment=ft.alignment.center),
            ], spacing=4),
            padding=10,
            bgcolor=ft.colors.GREY_800,
            border_radius=10,
            width=250,
            alignment=ft.alignment.center,
        )

    else:
        return ft.Container(
            content=ft.Column([
                ft.Container(content=ft.Text(f"{data.plate}", size=30, weight=ft.FontWeight.BOLD,  text_align=ft.TextAlign.CENTER), alignment=ft.alignment.center),
                # Imagen de no autorizada
                ft.Container(
                    content=ft.Image(src_base64=data.image, width=200, height=150, fit=ft.ImageFit.CONTAIN, repeat=ft.ImageRepeat.NO_REPEAT),
                    alignment=ft.alignment.center,
                    border_radius=8,
                ),

                # Fecha y Hora en fila con fondo
                ft.Row([
                    ft.Container(
                        content=ft.Text(f"Fecha: {format_date(data.created_at)}", size=size_font),
                        padding=ft.padding.all(8),  # Ajuste aquí
                        bgcolor=ft.colors.GREY_600,
                        border_radius=5,
                    ),
                    ft.Container(
                        content=ft.Text(f"Hora: {get_hours(data.created_at)}", size=size_font),
                        padding=ft.padding.all(8),  # Ajuste aquí
                        bgcolor=ft.colors.GREY_600,
                        border_radius=5,
                    ),
                ], spacing=10, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

                # Mensaje de no autorizado
                ft.Container(
                    content=ft.Text("NO AUTORIZADA", size=26, color=ft.colors.RED),
                    alignment=ft.alignment.center,
                    padding=ft.padding.all(10),  # Ajuste aquí
                    bgcolor=ft.colors.RED_50,
                    border_radius=8,
                ),
            ], spacing=4),
            padding=10,
            bgcolor=ft.colors.GREY_800,
            border_radius=10,
            width=250,
            alignment=ft.alignment.center,
            animate=ft.animation.Animation(1000, ft.AnimationCurve.BOUNCE_OUT),
        )


def view_image(page,id):
    history = history_service.get_history(id)
    card.content = generate_card(history)
    card.update()
    page.update()

def get_histories(page):
    global date_value
    rows.clear()
    histories = history_service.get_histories()
    filtered_histories = [
            entry for entry in histories
            if (not input_search.value or input_search.value.lower() in entry.plate.lower())  # Filtrado por placa
            and (personal_filter.value == "Todos" or  # Filtrado por personal (opcional)
                 (personal_filter.value == "Docente" and getattr(entry.vehicle, 'personal', None) == True) or
                 (personal_filter.value == "Estudiante" and getattr(entry.vehicle, 'personal', None) == False))
            and (check_authorized.value and check_not_authorized.value or  # Filtrado por autorización
                 check_authorized.value and entry.authorized == True or
                 check_not_authorized.value and entry.authorized == False)
            and (not date_value or date_value == entry.created_at.date())  # Filtrado por fecha
        ]

    for entry in filtered_histories:
        if(entry.authorized):
            image_driver = ft.Image(src_base64=encode_image_to_base64(default_image), width=100, height=100)
            image_icon_driver =os.path.join(folder_name_drivers, f"{entry.vehicle.plate}_driver.jpg")
            if os.path.exists(image_icon_driver):
                image_driver.src_base64 = encode_image_to_base64(image_icon_driver)

            rows.append(ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(str(entry.id))),
                    ft.DataCell(ft.Text(entry.plate)),
                    ft.DataCell(ft.Text(format_date(entry.created_at))),
                    ft.DataCell(ft.Text(get_hours(entry.created_at))),
                    ft.DataCell(ft.Row([
                        ft.Icon(name=ft.icons.ARROW_CIRCLE_RIGHT if entry.type == "Entrada" else ft.icons.ARROW_CIRCLE_LEFT, color="green" if entry.type == "Entrada" else "red"),
                        ft.Text(entry.type)
                    ])),
                    ft.DataCell(ft.Row([
                        image_driver,
                        ft.Text(f"{entry.vehicle.first_name} {entry.vehicle.last_name}")
                    ])),
                    ft.DataCell(ft.Text(entry.vehicle.ci)),
                    ft.DataCell(ft.Text(entry.vehicle.personal)),
                    ft.DataCell(ft.Text(entry.vehicle.make)),
                    ft.DataCell(ft.Text(entry.vehicle.color)),
                    ft.DataCell(ft.Row([
                        ft.IconButton(ft.icons.VISIBILITY, on_click=lambda e,id=entry.id: view_image(page,id)),
                    ]))
                ],color=ft.colors.GREEN_500
            ))
        else:
            rows.append(ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(str(entry.id))),
                    ft.DataCell(ft.Text(entry.plate)),
                    ft.DataCell(ft.Text(format_date(entry.created_at))),
                    ft.DataCell(ft.Text(get_hours(entry.created_at))),
                    ft.DataCell(ft.Row([
                        ft.Icon(name=ft.icons.ARROW_CIRCLE_RIGHT if entry.type == "Entrada" else ft.icons.ARROW_CIRCLE_LEFT, color="green" if entry.type == "Entrada" else "red"),
                        ft.Text(entry.type)
                    ])),
                    ft.DataCell(ft.Text("")),
                    ft.DataCell(ft.Text("")),
                    ft.DataCell(ft.Text("")),
                    ft.DataCell(ft.Text("")),
                    ft.DataCell(ft.Text("")),
                    ft.DataCell(ft.Row([
                        ft.IconButton(ft.icons.VISIBILITY, on_click=lambda e, id= entry.id: view_image(page,id)),
                    ]))
                ],color=ft.colors.RED_500
            ))

    page.update()

def download_data(path):
    global date_value
    wb = Workbook()
    ws = wb.active
    if ws is None:
        ws = wb.create_sheet()
    ws.title = "Historial de Entrada"
    ws.append(["Id", "Placa", "Fecha", "Hora", "Tipo", "Conductor", "Marca de Vehículo", "Color de Vehículo" ])
    if(not history_auth.value):
        rows = [entry for entry in history_service.get_histories_not_autorized(date_value) if input_search.value.lower() in entry.plate.lower()]
    else:
        rows = [entry for entry in history_service.get_histories_autorized(date_value) if input_search.value.lower() in entry.plate.lower()]

    for entry in rows:
        if entry.authorized:
            ws.append([str(entry.id), entry.plate, format_date(entry.created_at), get_hours(entry.created_at), entry.type, entry.vehicle.first_name + " "+ entry.vehicle.last_name, entry.vehicle.make , str(entry.vehicle.color)])
        else:
            ws.append([str(entry.id), entry.plate, format_date(entry.created_at), get_hours(entry.created_at), entry.type, "" , "", ""])
    name = "Entrada_" + format_date(date_value).replace("/", "-")
    full_path = os.path.join(path, name + ".xlsx")
    wb.save(full_path)

def get_directory_result(path):
    download_data(path.path)

def history_page(page: ft.Page):
    def filter(event):
        get_histories(page)

    def clear(event):
        global date_value
        date_text.value = datetime.now().date()
        date_value = datetime.now().date()
        get_histories(page)
        page.update()

    def select_date(event):
        global date_value
        date_text.value = event.control.value.strftime('%d/%m/%Y')
        date_value = event.control.value.date()
        page.update()

    title = ft.Text("Historial de entrada", theme_style=ft.TextThemeStyle.HEADLINE_MEDIUM)
    button_filter = ft.ElevatedButton("Filtrar", icon=ft.icons.FILTER, on_click=filter)
    button_clear = ft.ElevatedButton("Limpiar", icon=ft.icons.CLEAR, on_click=clear)
    date_picker = ft.Row([ft.ElevatedButton("Ingresar Fecha",icon=ft.icons.CALENDAR_MONTH,on_click=lambda e: page.open(ft.DatePicker(on_change=select_date)))])
    get_directory_dialog = ft.FilePicker(on_result=get_directory_result)
    page.overlay.extend([get_directory_dialog])
    get_histories(page)
    return ft.Column([ft.Row([
            ft.Column([
            title,
            ft.Row([
                ft.ElevatedButton(
                    "Descargar",
                    icon=ft.icons.DOWNLOAD,
                    on_click=lambda _: get_directory_dialog.get_directory_path(),
                    disabled=page.web,
                ),
            ], spacing=20),
            ft.Column([
                ft.Row([
                    ft.Stack(
                    height=500,
                    controls=[
                        ft.Column([
                            ft.DataTable(
                                column_spacing=20,
                                columns=columns,
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
        expand=True
        ),
        ft.VerticalDivider(width=2),
        ft.Column([
            ft.Column([
                input_search,
                ft.Row([date_picker, date_text]),
                personal_filter,
                check_authorized,
                check_not_authorized,
                ft.Row([button_filter, button_clear])
            ],spacing=20),
            ft.Container(
                card
            )
        ],width=300)
    ])])

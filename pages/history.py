import flet as ft
from services.history_service import HistoryService
from datetime import datetime
import openpyxl
from openpyxl import Workbook
import os

default_image = os.path.join("..", "assets", "icon.png")
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
    ft.DataColumn(ft.Text("Marca de Vehículo")),
    ft.DataColumn(ft.Text("Color de Vehículo")),
    ft.DataColumn(ft.Text("Acciones"))
]
size_font=9

input_search = ft.TextField(label="Buscar", icon=ft.icons.SEARCH,expand=True)
personal_filter = ft.Dropdown(label="Personal", value="Todos", options=[ft.dropdown.Option("Todos"), ft.dropdown.Option("Docente"), ft.dropdown.Option("Estudiante")],expand=True)
check_authorized = ft.Checkbox(label="Autorizados", value=True,expand=True)
check_not_authorized = ft.Checkbox(label="No Autorizados", value=False,expand=True)
card = ft.Card(content=ft.Text(""), expand=True)

def generate_card(data):
    if data.authorized:
        file = os.path.join(folder_name_drivers, f"{data.vehicle.plate}_driver.jpg")
        if data.type == "Salida":
            color = ft.colors.REED_200
        else:
            color = ft.colors.GREEN_200
        return ft.Container(ft.Column([
            ft.Text(data.plate, size=30),
            ft.Container(
                content=ft.Image(src_base64=data.image, width=200, height=150, fit=ft.ImageFit.CONTAIN,repeat=ft.ImageRepeat.NO_REPEAT),
                alignment=ft.alignment.center,
            ),
            ft.Row([
                ft.Text(f"Fecha: {format_date(data.created_at)}", size=size_font),
                ft.Text(f"Hora: {get_hours(data.created_at)}", size=size_font),
                ], spacing=1, alignment=ft.MainAxisAlignment.SPACE_BETWEEN )
            ,
            ft.Row([
                ft.Container(
                    content=ft.Image(src=file, width=100, fit=ft.ImageFit.CONTAIN,repeat=ft.ImageRepeat.NO_REPEAT),
                    alignment=ft.alignment.center,
                ),
                ft.Column([
                    ft.Text(f"Marca: {data.vehicle.make}", size=size_font),
                    ft.Text(f"Color: {data.vehicle.color}", size=size_font),
                ])
            ]),
            ft.Row([
                ft.Text(f"Nombre: {data.vehicle.first_name} {data.vehicle.last_name}", size=size_font),
                ft.Text(f"Personal: {data.vehicle.personal}", size=size_font),
                ft.Text(f"CI: {data.vehicle.ci}", size=size_font),
            ],),
            ft.Text(f"{data.type}", size=size_font)],
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),padding=20)
    else:
        return ft.Container(ft.Column([
            ft.Text(data.plate, size=30),
            ft.Container(
                content=ft.Image(src_base64=data.image, width=200, height=150, fit=ft.ImageFit.CONTAIN,repeat=ft.ImageRepeat.NO_REPEAT),
                alignment=ft.alignment.center,
            ),
            ft.Row([
                ft.Text(f"Fecha: {format_date(data.created_at)}", size=size_font),
                ft.Text(f"Hora: {get_hours(data.created_at)}", size=size_font),
                ], wrap=True, spacing=1, run_spacing=1, alignment=ft.MainAxisAlignment.SPACE_BETWEEN )
            ,
            ft.Container(
                content=ft.Text("NO AUTORIZADA", size=30),
                alignment=ft.alignment.center,
            )
            ],
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),padding=20)

def view_image(page,id):
    print(id)
    history = history_service.get_history(id)
    card.content = generate_card(history)
    if(history.authorized):
        card.color = ft.colors.GREEN_200
    else:
        card.color = ft.colors.RED_200
    card.update()
    page.update()

def get_histories(page):
    rows.clear()
    histories = history_service.get_histories()
    if(input_search.value):
        histories = [entry for entry in histories if input_search.value.lower() in entry.plate.lower()]

    if(personal_filter.value == "Todos"):
        pass
    elif(personal_filter.value == "Docente"):
        histories = [entry for entry in histories if entry.vehicle.personal == True]
    elif(personal_filter.value == "Estudiante"):
        histories = [entry for entry in histories if entry.vehicle.personal == False]

    if(check_authorized.value and check_not_authorized.value):
        pass

    elif(check_authorized.value):
        histories = [entry for entry in histories if entry.authorized == True]

    elif(check_not_authorized.value):
        histories = [entry for entry in histories if entry.authorized == False]

    if(date_value):
        histories = [entry for entry in histories if date_value == entry.created_at.date()]

    for entry in histories:
        print(entry.id)
        if(entry.authorized):
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
                    ft.DataCell(ft.Text(f"{entry.vehicle.first_name} {entry.vehicle.last_name}")),
                    ft.DataCell(ft.Text(entry.vehicle.make)),
                    ft.DataCell(ft.Text(entry.vehicle.color)),
                    ft.DataCell(ft.Row([
                        ft.IconButton(ft.icons.VISIBILITY, on_click=lambda e,id=entry.id: view_image(page,id)),
                    ]))
                ],color=ft.colors.GREEN_200
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
                    ft.DataCell(ft.Row([
                        ft.IconButton(ft.icons.VISIBILITY, on_click=lambda e, id= entry.id: view_image(page,id)),
                    ]))
                ],color=ft.colors.RED_200
            ))

    page.update()

def download_data(path):
    wb = Workbook()
    ws = wb.active
    if ws is None:
        ws = wb.create_sheet()
    ws.title = "Historial de Entrada"
    ws.append(["Id", "Placa", "Fecha", "Hora", "Tipo", "Conductor", "Modelo de Vehículo", "Color de Vehículo" ])
    name = "Entrada_Autorizados" if history_auth.value else "Entrada_No_Autorizados"
    if(not history_auth.value):
        rows = [entry for entry in history_service.get_histories_not_autorized(date_value) if text_value in entry.plate.lower()]
    else:
        rows = [entry for entry in history_service.get_histories_autorized(date_value) if text_value in entry.plate.lower()]
    for entry in rows:
        ws.append([str(entry.id), entry.plate, format_date(entry.created_at), get_hours(entry.created_at), entry.type, entry.vehicle.driver, entry.vehicle.model, str(entry.vehicle.color)])
    name += "_" + format_date(date_value)
    full_path = os.path.join(path, name + ".xlsx")
    wb.save(full_path)

def get_directory_result(path):
    download_data(path.path)

def history_page(page: ft.Page):
    def filter(event):
        get_histories(page)

    def clear(event):
        date_text.value = datetime.now().date()
        date_value = datetime.now().date()
        get_histories(page)
        page.update()

    def select_date(event):
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
                    height = 300,
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

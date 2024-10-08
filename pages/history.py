import flet as ft
from services.history_service import HistoryService
from datetime import datetime
import openpyxl
from openpyxl import Workbook
import os

def format_date(date):
    return date.strftime("%d/%m/%Y")

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
    ft.DataColumn(ft.Text("Modelo de Vehículo")),
    ft.DataColumn(ft.Text("Color de Vehículo")),
    ft.DataColumn(ft.Text("Acciones"))
]
def get_hours(date):
    return date.strftime("%H:%M")

def view_image(page,id):
    def close_modal(e):
        page.dialog.open = False
        page.update()
    image = history_service.get_history_image(id)
    modal = ft.AlertDialog(
        title=ft.Text("Imagen de entrada"),
        content=ft.Image(src_base64=image),
        actions=[ft.ElevatedButton("Cerrar", on_click=lambda e: close_modal(e))]
    )

    page.dialog = modal
    modal.open = True
    page.update()
def get_histories(page):
    rows.clear()
    if(history_auth.value):
        history = history_service.get_histories_autorized(date_value)
        for entry in history:
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
                    ft.DataCell(ft.Text(entry.vehicle.driver)),
                    ft.DataCell(ft.Text(entry.vehicle.model)),
                    ft.DataCell(ft.Text(str(entry.vehicle.color))),
                    ft.DataCell(ft.Row([
                        ft.IconButton(ft.icons.VISIBILITY, on_click=lambda e: view_image(page,entry.id)),
                    ]))
                ]
            ))
    else:
        history = history_service.get_histories_not_autorized(date_value)
        for entry in history:
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
                        ft.IconButton(ft.icons.VISIBILITY, on_click=lambda e: view_image(page,entry.id)),
                    ]))
                ]
            ))

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
    def on_search_change(event):
        global text_value, date_value
        value = event.control.value
        if(type(value) == datetime):
            date_text.value = "Fecha: " + format_date(value)
            date_value = value.date()
        else:
            text_value = value.lower()

        if(not history_auth.value):
            filtered_histories = [entry for entry in history_service.get_histories_not_autorized(date_value) if text_value in entry.plate.lower()]
        else:
            filtered_histories = [entry for entry in history_service.get_histories_autorized(date_value) if text_value in entry.plate.lower()]
        rows.clear()
        if(not history_auth.value):
            for entry in filtered_histories:
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
                            ft.IconButton(ft.icons.VISIBILITY, on_click=lambda e: view_image(page,entry.id)),
                        ]))
                    ]
                ))
        else:
            for entry in filtered_histories:
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
                        ft.DataCell(ft.Text(entry.vehicle.driver)),
                        ft.DataCell(ft.Text(entry.vehicle.model)),
                        ft.DataCell(ft.Text(str(entry.vehicle.color))),
                        ft.DataCell(ft.Row([
                            ft.IconButton(ft.icons.VISIBILITY, on_click=lambda e: view_image(page,entry.id)),
                        ]))
                    ]
                ))
        page.update()

    def on_change_switch(event):
        history_auth.label = "Autorizados" if history_auth.value else "No Autorizados"
        get_histories(page)
        page.update()
    title = ft.Text("Historial de entrada", theme_style=ft.TextThemeStyle.HEADLINE_MEDIUM)
    input_search = ft.TextField(label="Buscar", on_submit=on_search_change, icon=ft.icons.SEARCH)
    history_auth.on_change = on_change_switch
    date_picker = ft.Row([ft.ElevatedButton("Ingresar Fecha",icon=ft.icons.CALENDAR_MONTH,on_click=lambda e: page.open(ft.DatePicker(on_change=on_search_change))),date_text])
    get_histories(page)
    get_directory_dialog = ft.FilePicker(on_result=get_directory_result)
    page.overlay.extend([get_directory_dialog])
    return ft.Column([
        title,
        ft.Row([input_search, history_auth,date_picker,
            ft.ElevatedButton(
                "Descargar",
                icon=ft.icons.DOWNLOAD,
                on_click=lambda _: get_directory_dialog.get_directory_path(),
                disabled=page.web,
            ),
        ], spacing=20),
        ft.ListView([ ft.DataTable(
            width=800,
            columns= columns,
            rows=rows,
            expand=True,
        )],expand=1, spacing=10, padding=20, auto_scroll=True)
    ],
    expand=True
    )

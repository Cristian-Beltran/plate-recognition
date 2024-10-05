import flet as ft
from services.history_service import HistoryService

history_service = HistoryService()
history_auth = ft.Switch(label="Autorizados", value=True, )
rows = []

columns=[
    ft.DataColumn(ft.Text("Id"), numeric=True),
    ft.DataColumn(ft.Text("Placa")),
    ft.DataColumn(ft.Text("Fecha")),
    ft.DataColumn(ft.Text("Conductor")),
    ft.DataColumn(ft.Text("Modelo de Vehículo")),
    ft.DataColumn(ft.Text("Año de Vehículo")),
    ft.DataColumn(ft.Text("Acciones"))
]
def format_date(date):
    return date.strftime("%d/%m/%Y %H:%M")

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
        history = history_service.get_histories_autorized()
        for entry in history:
            rows.append(ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(str(entry.id))),
                    ft.DataCell(ft.Text(entry.plate)),
                    ft.DataCell(ft.Text(format_date(entry.created_at))),
                    ft.DataCell(ft.Text(entry.vehicle.driver)),
                    ft.DataCell(ft.Text(entry.vehicle.model)),
                    ft.DataCell(ft.Text(str(entry.vehicle.year))),
                    ft.DataCell(ft.Row([
                        ft.IconButton(ft.icons.VISIBILITY, on_click=lambda e: view_image(page,entry.id)),
                    ]))
                ]
            ))
    else:
        history = history_service.get_histories_not_autorized()
        for entry in history:
            rows.append(ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(str(entry.id))),
                    ft.DataCell(ft.Text(entry.plate)),
                    ft.DataCell(ft.Text(format_date(entry.created_at))),
                    ft.DataCell(ft.Text("")),
                    ft.DataCell(ft.Text("")),
                    ft.DataCell(ft.Text("")),
                    ft.DataCell(ft.Row([
                        ft.IconButton(ft.icons.VISIBILITY, on_click=lambda e: view_image(page,entry.id)),
                    ]))
                ]
            ))


def history_page(page: ft.Page):
    def on_search_change(event):
        search_term = event.control.value.lower()
        if(not history_auth.value):
            filtered_histories = [entry for entry in history_service.get_histories_not_autorized() if search_term in entry.plate.lower()]
        else:
            filtered_histories = [entry for entry in history_service.get_histories_autorized() if search_term in entry.plate.lower()]
        rows.clear()
        if(not history_auth.value):
            for entry in filtered_histories:
                rows.append(ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(entry.id))),
                        ft.DataCell(ft.Text(entry.plate)),
                        ft.DataCell(ft.Text(format_date(entry.created_at))),
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
                        ft.DataCell(ft.Text(entry.vehicle.driver)),
                        ft.DataCell(ft.Text(entry.vehicle.model)),
                        ft.DataCell(ft.Text(str(entry.vehicle.year))),
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
    get_histories(page)
    return ft.Column([
        title,
        ft.Row([input_search, history_auth], spacing=20),
        ft.ListView([ ft.DataTable(
            width=800,
            columns= columns,
            rows=rows,
            expand=True,
        )],expand=1, spacing=10, padding=20, auto_scroll=True)
    ],
    expand=True
    )

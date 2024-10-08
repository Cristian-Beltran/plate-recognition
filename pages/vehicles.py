import flet as ft
from services.vehicles_service import VehiclesService

vehicle_service = VehiclesService()
rows = []
make = ft.Dropdown(label="Marca", options=[
    ft.dropdown.Option("Toyota"),
    ft.dropdown.Option("Ford"),
    ft.dropdown.Option("Chevrolet"),
    ft.dropdown.Option("Honda"),
    ft.dropdown.Option("BMW"),
    ft.dropdown.Option("Mercedes-Benz"),
    ft.dropdown.Option("Audi"),
    ft.dropdown.Option("Nissan"),
    ft.dropdown.Option("Hyundai"),
    ft.dropdown.Option("Volkswagen"),
    ft.dropdown.Option("Kia"),
    ft.dropdown.Option("Subaru"),
    ft.dropdown.Option("Mazda"),
    ft.dropdown.Option("Tesla"),
    ft.dropdown.Option("Jeep"),
    ft.dropdown.Option("Volvo"),
    ft.dropdown.Option("Porsche"),
    ft.dropdown.Option("Lexus"),
    ft.dropdown.Option("Jaguar"),
    ft.dropdown.Option("Land Rover")
])
model = ft.TextField(label="Modelo")
year = ft.TextField(label="Año")
color = ft.TextField(label="Color")
plate = ft.TextField(label="Placa")
driver = ft.TextField(label="Conductor")
cellphone = ft.TextField(label="Teléfono")
license = ft.TextField(label="Licencia")


def validate_form():
    if not make.value:
        make.error_text = "El campo 'Marca' es obligatorio"
        return False
    else:
        make.error_text = None
    if not model.value:
        model.error_text = "El campo 'Modelo' es obligatorio"
        return False
    else:
        model.error_text = None
    if not year.value:
        year.error_text = "El campo 'Año' es obligatorio"
        return False
    else:
        year.error_text = None
    if not color.value:
        color.error_text = "El campo 'Color' es obligatorio"
        return False
    else:
        color.error_text = None
    if not plate.value:
        plate.error_text = "El campo 'Placa' es obligatorio"
        return False
    else:
        plate.error_text = None
    if not driver.value:
        driver.error_text = "El campo 'Conductor' es obligatorio"
        return False
    else:
        driver.error_text = None
    if not cellphone.value:
        cellphone.error_text = "El campo 'Teléfono' es obligatorio"
        return False
    else:
        cellphone.error_text = None
    if not license.value:
        license.error_text = "El campo 'Licencia' es obligatorio"
        return False
    else:
        license.error_text = None
    return True

def get_vehicles(page):
    rows.clear()
    vehicles = vehicle_service.get_vehicles()
    for vehicle in vehicles:
        rows.append(ft.DataRow(
            cells=[
                ft.DataCell(ft.Text(vehicle.make)),
                ft.DataCell(ft.Text(vehicle.model)),
                ft.DataCell(ft.Text(str(vehicle.year))),
                ft.DataCell(ft.Text(vehicle.color)),
                ft.DataCell(ft.Text(vehicle.plate)),
                ft.DataCell(ft.Text(vehicle.driver)),
                ft.DataCell(ft.Text(vehicle.cellphone)),
                ft.DataCell(ft.Text(vehicle.license)),
                ft.DataCell(ft.Row([
                    ft.IconButton(ft.icons.EDIT, on_click=lambda e: update_vehicle_modal(page,vehicle.plate)),
                    ft.IconButton(ft.icons.DELETE, on_click=lambda e: delete_vehicle_modal(page,vehicle.plate))
                ]))
            ]
        ))

def clear_form():
    make.value = ""
    model.value = ""
    year.value = ""
    color.value = ""
    plate.value = ""
    driver.value = ""
    cellphone.value = ""
    license.value = ""

def add_vehicle_modal(page: ft.Page):
    clear_form()
    def close_modal(e):
        page.dialog.open = False
        page.update()

    def add_vehicle(e):
        if(not validate_form()):
            page.update()
            return
        vehicle_service.create_vehicle(make.value, model.value, year.value, color.value, plate.value, driver.value, cellphone.value, license.value)
        get_vehicles(page)
        page.update()
        close_modal(e)

    modal = ft.AlertDialog(
        title=ft.Text("Agregar Nuevo Vehiculo"),
        content=ft.Column([
            make,
            model,
            year,
            color,
            plate,
            driver,
            cellphone,
            license,
        ]),
        actions=[ft.ElevatedButton("Agregar", on_click=add_vehicle),ft.TextButton("Cerrar", on_click=close_modal)]
    )
    page.dialog = modal
    modal.open = True
    page.update()

def update_vehicle_modal(page,vehicle_id):
    clear_form()
    vehicle = vehicle_service.get_vehicle_by_id(vehicle_id)
    make.value = vehicle.make
    model.value = vehicle.model
    year.value = str(vehicle.year)
    color.value = vehicle.color
    plate.value = vehicle.plate
    driver.value = vehicle.driver
    cellphone.value = vehicle.cellphone
    license.value = vehicle.license

    def close_modal(e):
        page.dialog.open = False
        page.update()

    def update_vehicle(vehicle_id):
        if(not validate_form()):
            page.update()
            return
        vehicle_service.update_vehicle(vehicle_id, make=make.value, model=model.value, year=int(year.value), color=color.value, plate=plate.value, driver=driver.value, cellphone=cellphone.value, license=license.value)
        get_vehicles(page)
        page.dialog.open = False
        page.update()

    modal = ft.AlertDialog(
        title=ft.Text("Editar Vehicle"),
        content=ft.Column([
            make,
            model,
            year,
            color,
            plate,
            driver,
            cellphone,
            license,
        ]),
        actions=[ft.ElevatedButton("Editar", on_click=lambda e: update_vehicle(vehicle_id)) ,ft.TextButton("Cerrar", on_click=lambda e: close_modal(e))]
    )
    page.dialog = modal
    modal.open = True
    page.update()

def delete_vehicle_modal(page, vehicle_id):
    def close_modal(e):
        page.dialog.open = False
        page.update()
    def delete_vehicle(vehicle_id):
        vehicle_service.delete_vehicle(vehicle_id)
        get_vehicles(page)
        page.dialog.open = False
        page.update()

    modal = ft.AlertDialog(
        title=ft.Text("Eliminar Vehiculo"),
        content=ft.Text("¿Está seguro de eliminar este vehiculo?"),
        actions = [ft.ElevatedButton("Eliminar", on_click=lambda e: delete_vehicle), ft.TextButton("Cancelar", on_click=lambda e: close_modal(e))]
    )
    page.dialog = modal
    modal.open = True
    page.update()

def vehicles_page(page: ft.Page):
    def on_search_change(e):
        search_term = e.control.value.lower()
        filtered_vehicles = [v for v in vehicle_service.get_vehicles() if search_term in v.plate.lower()]
        rows.clear()
        for vehicle in filtered_vehicles:
            rows.append(ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(str(vehicle.id))),
                    ft.DataCell(ft.Text(vehicle.make)),
                    ft.DataCell(ft.Text(vehicle.model)),
                    ft.DataCell(ft.Text(str(vehicle.year))),
                    ft.DataCell(ft.Text(vehicle.color)),
                    ft.DataCell(ft.Text(vehicle.plate)),
                    ft.DataCell(ft.Text(vehicle.driver)),
                    ft.DataCell(ft.Text(vehicle.cellphone)),
                    ft.DataCell(ft.Text(vehicle.license)),
                    ft.DataCell(ft.Row([
                        ft.IconButton(ft.icons.EDIT, on_click=lambda e, id=vehicle.id: update_vehicle_modal(page, id)),
                        ft.IconButton(ft.icons.DELETE, on_click=lambda e, id=vehicle.id: delete_vehicle_modal(page, id))
                    ]))
                ]
            ))
        page.update()
    def on_add_vehicle_click(e):
        add_vehicle_modal(page)
    title = ft.Text("Vehiculos", theme_style=ft.TextThemeStyle.HEADLINE_MEDIUM)
    input_search = ft.TextField(label="Buscar", on_submit=on_search_change, icon=ft.icons.SEARCH)
    add_vehicle = ft.IconButton(icon=ft.icons.ADD,icon_color="blue400", on_click=on_add_vehicle_click,tooltip="Agregar usuario")
    get_vehicles(page)
    return ft.Column([
        title,
        ft.Row([
            input_search,
            add_vehicle,
        ], spacing=20),
        ft.ListView([ft.DataTable(width=800, columns=[
            ft.DataColumn(ft.Text("Marca"), numeric=False),
            ft.DataColumn(ft.Text("Modelo"), numeric=False),
            ft.DataColumn(ft.Text("Año"), numeric=False),
            ft.DataColumn(ft.Text("Color"), numeric=False),
            ft.DataColumn(ft.Text("Placa"), numeric=False),
            ft.DataColumn(ft.Text("Conductor"), numeric=False),
            ft.DataColumn(ft.Text("Teléfono"), numeric=False),
            ft.DataColumn(ft.Text("Licencia"), numeric=False),
            ft.DataColumn(ft.Text("Acciones"), numeric=False)
        ], rows=rows, expand=True)], expand=1, spacing=10, padding=20, auto_scroll=True)
    ],expand=True)

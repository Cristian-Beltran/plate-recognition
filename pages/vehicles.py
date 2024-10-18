import flet as ft
from services.vehicles_service import VehiclesService
import shutil
import os

vehicle_service = VehiclesService()
rows = []
plate = ft.TextField(label="Placa",expand=True)
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
],expand=True)
color = ft.TextField(label="Color",expand=True)
first_name = ft.TextField(label="Nombre",expand=True)
last_name = ft.TextField(label="Apellido",expand=True)
cellphone = ft.TextField(label="Teléfono",expand=True)
ci = ft.TextField(label="CI",expand=True)
personal = ft.Dropdown(label="Personal", options=[
    ft.dropdown.Option("Estudiante"),
    ft.dropdown.Option("Docente")
],expand=True)
default_image = os.path.join("..", "assets", "icon.png")
vehicle_image = ft.Image(src=default_image, width=100, height=100)
driver_image = ft.Image(src=default_image, width=100, height=100)
vehicle_global_id = None

folder_name_vehicles = "vehicles_images"
folder_name_drivers = "drivers_images"

if not os.path.exists(folder_name_vehicles):
    os.makedirs(folder_name_vehicles)

if not os.path.exists(folder_name_drivers):
    os.makedirs(folder_name_drivers)

selected_image_path_vehicle = None
selected_image_path_driver = None


def vehicles_page(page: ft.Page):
    def upload_image_vehicle(e):
        global selected_image_path_vehicle
        selected_image_path_vehicle = e.files[0].path
        if selected_image_path_vehicle:
            # Mostrar la imagen en la app
            vehicle_image.src = selected_image_path_vehicle
            page.update()
    def upload_image_driver(e):
        global selected_image_path_driver
        selected_image_path_driver = e.files[0].path
        if selected_image_path_driver:
            # Mostrar la imagen en la app
            driver_image.src = selected_image_path_driver
            page.update()

    upload_file_dialog_vehicle = ft.FilePicker(on_result=upload_image_vehicle)
    upload_file_dialog_driver = ft.FilePicker(on_result=upload_image_driver)

    def handle_route_change(r: ft.RouteChangeEvent):
        if page.route == "/update":
            page.views.append(
                ft.View(
                    route="/update",
                    fullscreen_dialog=True,     # MAIN parameter for the full-screen dialog!
                    appbar=ft.AppBar(title=ft.Text("Editar Vehículo"),),
                    controls=[update_vehicle_modal()],
                )
            )
            page.update()
        if page.route == "/add":
            page.views.append(
                ft.View(
                    route="/add",
                    fullscreen_dialog=True,     # MAIN parameter for the full-screen dialog!
                    appbar=ft.AppBar(title=ft.Text("Crear Vehículo"),),
                    controls=[add_vehicle_modal()],
                )
            )
            page.update()
    def handle_view_pop(view: ft.ViewPopEvent):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    def on_add_vehicle_click(e: ft.ControlEvent):
        vehicle_image.src = default_image
        driver_image.src = default_image
        selected_image_path=None
        page.go("/add")
        page.update()

    def clear_form():
        plate.value = ""
        make.value = ""
        color.value = ""
        first_name.value = ""
        last_name.value = ""
        cellphone.value = ""
        ci.value = ""
        personal.value = ""

    def update_vehicle(vehicle_id):
        clear_form()
        global vehicle_global_id
        vehicle_global_id = vehicle_id
        vehicle = vehicle_service.get_vehicle_by_id(vehicle_id)
        make.value = vehicle.make
        color.value = vehicle.color
        first_name.value = vehicle.first_name
        last_name.value = vehicle.last_name
        cellphone.value = vehicle.cellphone
        ci.value = vehicle.ci
        personal.value = vehicle.personal
        vehicle_image.src = default_image
        driver_image.src = default_image
        selected_image_path=None
        file = os.path.join(folder_name_vehicles, f"{vehicle_global_id}.jpg")
        if os.path.exists(file):
            vehicle_image.src = file
        file = os.path.join(folder_name_drivers, f"{vehicle_global_id}.jpg")
        if os.path.exists(file):
            driver_image.src = file
        page.go("/update")
        page.update()

    def formate_date(date):
        if(date == None):
            return ""
        return date.strftime("%d/%m/%Y")

    def delete_vehicle(vehicle_id):
        vehicle_service.delete_vehicle(vehicle_id)
        get_vehicles()
        page.dialog.open = False
        page.update()

    def delete_vehicle_modal(vehicle_id):
        def close_modal(e):
            page.dialog.open = False
            page.update()
        modal = ft.AlertDialog(
            title=ft.Text("Eliminar Vehiculo"),
            content=ft.Text("¿Está seguro de eliminar este vehiculo?"),
            actions = [ft.ElevatedButton("Eliminar", on_click=lambda e, vehicle_id=vehicle_id: delete_vehicle(vehicle_id)), ft.TextButton("Cancelar", on_click=lambda e: close_modal(e))]
        )
        page.dialog = modal
        modal.open = True
        page.update()

    def get_vehicles():
        rows.clear()
        vehicles = vehicle_service.get_vehicles()
        for vehicle in vehicles:
            rows.append(ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(vehicle.plate)),
                    ft.DataCell(ft.Text(vehicle.make)),
                    ft.DataCell(ft.Text(vehicle.color)),
                    ft.DataCell(ft.Text(vehicle.first_name)),
                    ft.DataCell(ft.Text(vehicle.last_name)),
                    ft.DataCell(ft.Text(vehicle.ci)),
                    ft.DataCell(ft.Text(vehicle.cellphone)),
                    ft.DataCell(ft.Text(vehicle.personal)),
                    ft.DataCell(ft.Row([
                        ft.IconButton(ft.icons.EDIT, on_click=lambda e, id=vehicle.plate: update_vehicle(id)),
                        ft.IconButton(ft.icons.DELETE, on_click=lambda e, id=vehicle.plate: delete_vehicle_modal(id)),
                    ]))
                ]
            ))
    def validate_form():
        if not plate.value:
            plate.error_text = "El campo 'Placa' es obligatorio"
            return False
        else:
            plate.error_text = None
        if not make.value:
            make.error_text = "El campo 'Marca' es obligatorio"
            return False
        else:
            make.error_text = None
        if not color.value:
            color.error_text = "El campo 'Color' es obligatorio"
            return False
        else:
            color.error_text = None
        if not first_name.value:
            first_name.error_text = "El campo 'Nombre' es obligatorio"
            return False
        else:
            first_name.error_text = None
        if not last_name.value:
            last_name.error_text = "El campo 'Apellido' es obligatorio"
            return False
        else:
            last_name.error_text = None
        if not ci.value:
            ci.error_text = "El campo 'CI' es obligatorio"
            return False
        else:
            ci.error_text = None
        if not cellphone.value:
            cellphone.error_text = "El campo 'Teléfono' es obligatorio"
            return False
        else:
            cellphone.error_text = None
        if not personal.value:
            personal.error_text = "El campo 'Personal' es obligatorio"
            return False
        else:
            personal.error_text = None
        return True

    def update_vehicle_modal():
        global vehicle_global_id
        if (vehicle_global_id != None):
            return ft.Container()
        def close_modal(e):
            page.views.pop()
            top_view = page.views[-1]
            page.go(top_view.route)
        def add_vehicle(e):
            if(not validate_form()):
                page.update()
                return
            try:
                if(selected_image_path_vehicle):
                    new_image_name = f"{vehicle_global_id}_vehicle.jpg"
                    copy = os.path.join(folder_name_vehicles, new_image_name)
                    shutil.copyfile(selected_image_path_vehicle, copy)
                if(selected_image_path_driver):
                    new_image_name = f"{vehicle_global_id}_driver.jpg"
                    copy = os.path.join(folder_name_drivers, new_image_name)
                    shutil.copyfile(selected_image_path_driver, copy)
            except Exception as error:
                print(error)
            vehicle_service.update_vehicle(plate=plate.value, make=make.value, color=color.value, first_name=first_name.value, last_name=last_name.value, ci=ci.value, cellphone=cellphone.value, personal=personal.value)
            get_vehicles()
            page.update()
            close_modal(e)
        return ft.Container(
            ft.Column([
                ft.Row([
                    ft.Container(ft.Column([
                        ft.Text("Foto de conductor"),
                        driver_image,
                        ft.ElevatedButton("Subir Foto", on_click=lambda _: upload_file_dialog_driver.pick_files(allow_multiple=False))
                    ])),
                    ft.Column([
                        first_name,
                        last_name,
                    ],expand=True)
                ]),
                ft.Column([
                    ft.Row([
                        ci,
                        cellphone,
                        personal,
                    ]),
                ]),
                ft.Row([
                    ft.Container(ft.Column([
                        ft.Text("Foto de vehiculo"),
                        vehicle_image,
                        ft.ElevatedButton("Subir Foto", on_click=lambda _: upload_file_dialog_vehicle.pick_files(allow_multiple=False))
                    ])),
                    ft.Column([
                        make,
                        color,
                    ],expand=True)
                ]),
                ft.Column([
                    plate,
                ]),
                ft.Row([
                    ft.ElevatedButton("Actualizar", on_click=add_vehicle),
                    ft.TextButton("Cancelar", on_click=lambda e: close_modal(e))
                ])
            ],horizontal_alignment=ft.CrossAxisAlignment.CENTER, width=500),
            expand=True, alignment=ft.alignment.center
        )


    def add_vehicle_modal():
        clear_form()
        def close_modal(e):
            page.views.pop()
            top_view = page.views[-1]
            page.go(top_view.route)
        def add_vehicle(e):
            if(not validate_form()):
                page.update()
                return
            vehicle_service.create_vehicle(plate=plate.value, make=make.value, color=color.value, first_name=first_name.value, last_name=last_name.value, ci=ci.value, cellphone=cellphone.value, personal=personal.value)
            vehicle = vehicle_service.get_last_vehicle()
            try:
                if(selected_image_path_vehicle):
                    new_image_name = f"{vehicle.plate}_vehicle.jpg"
                    copy = os.path.join(folder_name_vehicles, new_image_name)
                    shutil.copyfile(selected_image_path_vehicle, copy)
                if(selected_image_path_driver):
                    new_image_name = f"{vehicle.plate}_driver.jpg"
                    copy = os.path.join(folder_name_drivers, new_image_name)
                    shutil.copyfile(selected_image_path_driver, copy)
            except Exception as error:
                print(error)

            get_vehicles()
            page.update()
            close_modal(e)
        return ft.Container(
            ft.Column([
                ft.Row([
                    ft.Container(ft.Column([
                        ft.Text("Foto de conductor"),
                        driver_image,
                        ft.ElevatedButton("Subir Foto", on_click=lambda _: upload_file_dialog_driver.pick_files(allow_multiple=False))
                    ])),
                    ft.Column([
                        first_name,
                        last_name,
                    ],expand=True)
                ]),
                ft.Column([
                    ft.Row([
                        ci,
                        cellphone,
                        personal,
                    ]),
                ]),
                ft.Row([
                    ft.Container(ft.Column([
                        ft.Text("Foto de vehiculo"),
                        vehicle_image,
                        ft.ElevatedButton("Subir Foto", on_click=lambda _: upload_file_dialog_vehicle.pick_files(allow_multiple=False))
                    ])),
                    ft.Column([
                        make,
                        color,
                    ],expand=True)
                ]),
                ft.Column([
                    plate,
                ]),
                ft.Row([
                        ft.ElevatedButton("Agregar", on_click=add_vehicle),
                        ft.TextButton("Cancelar", on_click=lambda e: close_modal(e))
                ])
            ],horizontal_alignment=ft.CrossAxisAlignment.CENTER, width=500),
            expand=True, alignment=ft.alignment.center
        )

    def on_search_change(e):
        search_term = e.control.value.lower()
        filtered_vehicles = [v for v in vehicle_service.get_vehicles() if search_term in v.plate.lower()]
        rows.clear()
        for vehicle in filtered_vehicles:
            rows.append(ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(vehicle.plate)),
                    ft.DataCell(ft.Text(vehicle.make)),
                    ft.DataCell(ft.Text(vehicle.color)),
                    ft.DataCell(ft.Text(vehicle.first_name)),
                    ft.DataCell(ft.Text(vehicle.last_name)),
                    ft.DataCell(ft.Text(vehicle.ci)),
                    ft.DataCell(ft.Text(vehicle.cellphone)),
                    ft.DataCell(ft.Text(vehicle.personal)),
                    ft.DataCell(ft.Row([
                        ft.IconButton(ft.icons.EDIT, on_click=lambda e, id=vehicle.plate: update_vehicle(id)),
                        ft.IconButton(ft.icons.DELETE, on_click=lambda e, id=vehicle.id: delete_vehicle_modal(id))
                    ]))
                ]
            ))
        page.update()
    title = ft.Text("Vehiculos", theme_style=ft.TextThemeStyle.HEADLINE_MEDIUM)
    input_search = ft.TextField(label="Buscar", on_submit=on_search_change, icon=ft.icons.SEARCH)
    add_vehicle = ft.IconButton(icon=ft.icons.ADD,icon_color="blue400", on_click=on_add_vehicle_click,tooltip="Agregar usuario")
    page.on_route_change = handle_route_change
    page.on_view_pop = handle_view_pop
    page.overlay.extend([upload_file_dialog_vehicle, upload_file_dialog_driver])

    get_vehicles()
    return ft.Column([
        title,
        ft.Row([input_search, add_vehicle],spacing=20),
        ft.Column([
            ft.Row([
                ft.Stack(
                height = 300,
                controls=[
                    ft.Column([
                        ft.DataTable(
                            column_spacing=20,
                            columns=[
                                ft.DataColumn(ft.Text("Placa")),
                                ft.DataColumn(ft.Text("Marca")),
                                ft.DataColumn(ft.Text("Color")),
                                ft.DataColumn(ft.Text("Nombre")),
                                ft.DataColumn(ft.Text("Apellido")),
                                ft.DataColumn(ft.Text("CI")),
                                ft.DataColumn(ft.Text("Celular")),
                                ft.DataColumn(ft.Text("Personal")),
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

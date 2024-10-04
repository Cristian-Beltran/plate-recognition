import flet as ft

def history_page(page: ft.Page):
    return ft.Column([
        ft.Text("Apartado de historial"),
        ft.TextField(label="Dirección"),
        ft.TextField(label="Teléfono"),
        ft.ElevatedButton("Guardar", on_click=lambda e: print("Datos guardados"))
    ])

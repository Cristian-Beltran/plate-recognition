import cv2
import flet as ft
import threading
import time
import base64
from flet import Image
from services.vehicles_service import VehiclesService
from services.history_service import HistoryService

rows = []
camera_feed = Image(width=640, height=480, src=False, fit="cover")
list = ft.ListView(spacing=5, padding=10, auto_scroll=True,width=200)
card1 = ft.Card(content=ft.Text("Sin Datos"), expand=True)
card2 = ft.Card(content=ft.Text("Sin Datos"), expand=True)
card3 = ft.Card(content=ft.Text("Sin Datos"), expand=True)
service_history = HistoryService()

def add_history(page):
    service_history.create_history("123456789", camera_feed.src_base64)
    # Desplazar la información existente
    card3.content = card2.content
    card2.content = card1.content
    # Obtener la última historia agregada
    last_history = service_history.get_last_history()
    # Actualizar card1 con la nueva información
    if last_history.authorized:
        card1.color = ft.colors.GREEN
    else:
        card1.color = ft.colors.RED

    card1.content = ft.Column([
        Image(src_base64=last_history.image, width=200, height=150),
        ft.Text(f"Placa: {last_history.plate}"),
        ft.Text(f"Fecha: {last_history.created_at}")
    ])
    # Actualizar las tarjetas
    card1.update()
    card2.update()
    card3.update()
    # Actualizar la lista
    rows = service_history.get_histories_today()
    list.controls = [ft.Text(f"Placa: {row.plate} Autorizada: {row.authorized}") for row in rows[3:]]
    list.update()

def get_histories_today(page):
    rows = service_history.get_histories_today()
    # Mostrar las primeras 3 filas con imagen e información
    for i, row in enumerate(rows[:3]):
        if i == 0 and row.image is not None:
            card1.content = ft.Column([
                Image(src_base64=row.image, width=200, height=150),
                ft.Text(f"Placa: {row.plate}"),
                ft.Text(f"Fecha: {row.created_at}")
            ])
        elif i == 1 and row.image is not None:
            card2.content = ft.Column([
                Image(src_base64=row.image, width=200, height=150),
                ft.Text(f"Placa: {row.plate}"),
                ft.Text(f"Fecha: {row.created_at}")
            ])
        elif i == 2 and row.image is not None:
            card3.content = ft.Column([
                Image(src_base64=row.image, width=200, height=150),
                ft.Text(f"Placa: {row.plate}"),
                ft.Text(f"Fecha: {row.created_at}")
            ])
    list.controls = [ft.Text(f"Placa: {row.plate} Autorizada: {row.authorized}") for row in rows[3:]]
    page.update()

def capture_camera():
    cap = cv2.VideoCapture(0)  # 0 para la cámara por defecto
    while False:
        ret, frame = cap.read()
        if ret:
            try:
                # Convertir el frame capturado a formato JPEG en memoria
                _, img_encoded = cv2.imencode('.png', frame)
                img_base64 = base64.b64encode(img_encoded)
                camera_feed.src_base64 = img_base64.decode('utf-8')
                camera_feed.update()
            except Exception as e:
                print(f"Error al codificar la imagen: {e}")
        time.sleep(0.03)  # Actualizar cada 30 ms

def camera_page(page: ft.Page):
    title = ft.Text("Cámara", theme_style=ft.TextThemeStyle.HEADLINE_MEDIUM)
    thread = threading.Thread(target=capture_camera, daemon=True)
    thread.start()
    get_histories_today(page)
    return ft.Column([
        title,
        ft.Row([
            ft.Column([
                ft.Row([
                    ft.Card(
                        content=camera_feed,
                        height=400,
                        expand=True,
                    ),
                ]),
                ft.Row([
                    card1,
                    card2,
                    card3,
                ],expand=True)
            ], expand=True),
            ft.VerticalDivider(width=1),
            list,
            ft.IconButton(icon=ft.icons.ADD, on_click=add_history, tooltip="Agregar historia"),
        ], expand=True),
    ], expand=True)

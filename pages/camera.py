import cv2
import flet as ft
import threading
import time
import base64
from flet import Image
from services.vehicles_service import VehiclesService
from services.history_service import HistoryService

rows = []
stop_event = threading.Event()
size_image = 350
camera_thread = None
camera_feed = Image(width=640, height=480, src=False, fit="cover")
list = ft.ListView(spacing=5, padding=10, auto_scroll=False, width=200 )
card1 = ft.Card(content=ft.Text("Sin Datos"), )
card2 = ft.Card(content=ft.Text("Sin Datos"), )
card3 = ft.Card(content=ft.Text("Sin Datos"), )
service_history = HistoryService()
size_font = 10

def formated_date(date):
    return date.strftime("%d/%m/%Y %H:%M")

def add_history(page):
    service_history.create_history("123456789", camera_feed.src_base64)
    # Desplazar la información existente
    card3.content = card2.content
    card2.content = card1.content
    # Obtener la última historia agregada
    last_history = service_history.get_last_history()
    # Actualizar card1 con la nueva información
    if last_history.authorized:
        card1.color = ft.colors.GREEN_200
    else:
        card1.color = ft.colors.RED_200
    card1.content = ft.Column([
        ft.Container(
            content=Image(src_base64=last_history.image, width=200, height=150, fit=ft.ImageFit.CONTAIN,repeat=ft.ImageRepeat.NO_REPEAT, border_radius=ft.border_radius.all(10)),
            alignment=ft.alignment.center,
        ),
        ft.Container(ft.Column([
            ft.Text(f"Placa: {last_history.plate}", size=size_font),
            ft.Text(f"Fecha: {formated_date(last_history.created_at)}", size=size_font),
            ft.Text(f"Autorizada: {'Autorizada' if last_history.authorized else 'No autorizada'}", size=size_font)
        ], wrap=True, spacing=1, run_spacing=1 ), padding=ft.padding.all(10))
    ])
    card1.update()
    card2.update()
    card3.update()
    rows = service_history.get_histories_today()
    list.controls = [ft.Text(f"Placa: {row.plate} - {'Autorizada' if row.authorized else 'No autorizada'} - Fecha: {formated_date(row.created_at)}", size=size_font) for row in rows[3:]]
    list.update()

def get_histories_today(page):
    rows = service_history.get_histories_today()
    # Mostrar las primeras 3 filas con imagen e información
    for i, row in enumerate(rows[:3]):
        if i == 0 and row.image is not None:
            card1.content = ft.Column([
                ft.Container(
                    content=Image(src_base64=row.image, width=200, height=150, fit=ft.ImageFit.CONTAIN,repeat=ft.ImageRepeat.NO_REPEAT, border_radius=ft.border_radius.all(10)),
                    alignment=ft.alignment.center,
                ),
                ft.Container(ft.Column([
                    ft.Text(f"Placa: {row.plate}", size=size_font),
                    ft.Text(f"Fecha: {formated_date(row.created_at)}", size=size_font),
                    ft.Text(f"Autorizada: {'Autorizada' if row.authorized else 'No autorizada'}", size=size_font)
                ], wrap=True, spacing=1, run_spacing=1 ), padding=ft.padding.all(10))
            ])
        elif i == 1 and row.image is not None:
            card2.content = ft.Column([
                ft.Container(
                    content=Image(src_base64=row.image, width=200, height=150, fit=ft.ImageFit.CONTAIN,repeat=ft.ImageRepeat.NO_REPEAT, border_radius=ft.border_radius.all(10)),
                    alignment=ft.alignment.center,
                ),
                ft.Container(ft.Column([
                    ft.Text(f"Placa: {row.plate}", size=size_font),
                    ft.Text(f"Fecha: {formated_date(row.created_at)}", size=size_font),
                    ft.Text(f"Autorizada: {'Autorizada' if row.authorized else 'No autorizada'}", size=size_font)
                ], wrap=True, spacing=1, run_spacing=1 ), padding=ft.padding.all(10))
            ])
        elif i == 2 and row.image is not None:
            card3.content = ft.Column([
                ft.Container(
                    content=Image(src_base64=row.image, width=200, height=150, fit=ft.ImageFit.CONTAIN,repeat=ft.ImageRepeat.NO_REPEAT, border_radius=ft.border_radius.all(10)),
                    alignment=ft.alignment.center,
                ),
                ft.Container(ft.Column([
                    ft.Text(f"Placa: {row.plate}", size=size_font),
                    ft.Text(f"Fecha: {formated_date(row.created_at)}", size=size_font),
                    ft.Text(f"Autorizada: {'Autorizada' if row.authorized else 'No autorizada'}", size=size_font)
                ], wrap=True, spacing=1, run_spacing=1 ), padding=ft.padding.all(10))
            ],)
    list.controls = [ft.Text(f"Placa: {row.plate} - {'Autorizada' if row.authorized else 'No autorizada'} - Fecha: {formated_date(row.created_at)}", size=size_font) for row in rows[3:]]
    page.update()

def stop_camera():
    stop_event.set()

def capture_camera():
    cap = cv2.VideoCapture(0)  # 0 para la cámara por defecto
    while not stop_event.is_set():
        ret, frame = cap.read()
        if ret:
            try:
                # Convertir el frame capturado a formato JPEG en memoria
                _, img_encoded = cv2.imencode('.png', frame)
                img_base64 = base64.b64encode(img_encoded)
                camera_feed.src_base64 = img_base64.decode('utf-8')
                camera_feed.width = frame.shape[1]
                camera_feed.height = frame.shape[0]
                camera_feed.update()
            except Exception as e:
                print(f"Error al codificar la imagen: {e}")
        time.sleep(0.03)  # Actualizar cada 30 ms
    cap.release()


def camera_page(page: ft.Page):
    title = ft.Text("Cámara", theme_style=ft.TextThemeStyle.HEADLINE_MEDIUM)
    global camera_thread
    if camera_thread is None or not camera_thread.is_alive():
        # Reiniciamos el estado del evento para permitir que capture_camera vuelva a correr
        stop_event.clear()

        # Iniciamos el hilo de la cámara
        camera_thread = threading.Thread(target=capture_camera, daemon=True)
        camera_thread.start()
    get_histories_today(page)
    return ft.Column([
        title,
        ft.Row([
            ft.Column([
                ft.Row([
                    ft.Card(
                        content=camera_feed,
                        height=size_image,
                        expand=True,
                    ),
                ]),
                ft.Row([
                    card1,
                    card2,
                    card3,
                ],expand=True, alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            ], expand=True),
            ft.VerticalDivider(width=1),
            list,
            ft.IconButton(icon=ft.icons.ADD, on_click=add_history, tooltip="Agregar historia"),
        ], expand=True),
    ], expand=True)

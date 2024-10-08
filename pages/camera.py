import cv2
import pytesseract
import re
from ultralytics import YOLO
import flet as ft
import threading
import time
import base64
import os
from flet import Image
from services.vehicles_service import VehiclesService
from services.history_service import HistoryService
from datetime import datetime

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

try:
    model_path = os.path.join(os.path.dirname(__file__), "../model/runs/detect/train/weights/best.pt")
    model = YOLO(model_path)
except Exception as e:
    print(f"Error al cargar el modelo: {e}")
    exit()


def preprocess_image(img):
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray_img = cv2.blur(gray_img, (3, 3))
    return gray_img

# Redimensionar imagen de la placa para mejor reconocimiento
def resize_plate_image(img):
    return cv2.resize(img, (400, 100), interpolation=cv2.INTER_LINEAR)

# Filtro para texto de placas vehiculares (4 números y 3 letras)
def filter_plate_text(text):
    match = re.match(r'\d{4}[A-Z]{3}', text)
    if match:
        return match.group(0)
    return None

def formated_date(date):
    return date.strftime("%d/%m/%Y %H:%M")

def add_history(plate):
    history = service_history.create_history(plate, camera_feed.src_base64)
    if not history:
        return
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
    cap = cv2.VideoCapture(0)
    while not stop_event.is_set():
        ret, frame = cap.read()
        if ret:
            try:
                # Detectar las placas vehiculares en el frame
                results = model(frame)
                if(len(results) > 0):
                    for result in results:
                        boxes = result.boxes
                        if boxes is not None:
                            for box in boxes:
                                # Obtener las coordenadas del cuadro de la placa
                                x1, y1, x2, y2 = map(int, box.xyxy[0])
                                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)  # Dibuja un rectángulo sobre la placa
                                plate_img = frame[y1:y2, x1:x2]
                                plate_img = preprocess_image(plate_img)
                                text = pytesseract.image_to_string(plate_img, config='--psm 11 --oem 1').strip().upper()
                                filtered_text = filter_plate_text(text)
                                if filtered_text:
                                    add_history(text)
                                    cv2.putText(frame, text, (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
                # Actualizar el feed de la cámara en la interfaz
                _, img_encoded = cv2.imencode('.png', frame)
                img_base64 = base64.b64encode(img_encoded)
                camera_feed.src_base64 = img_base64.decode('utf-8')
                camera_feed.width = frame.shape[1]
                camera_feed.height = frame.shape[0]
                camera_feed.update()
            except Exception as e:
                print(f"Error al codificar la imagen: {e}")
        time.sleep(0.01)  # Actualizar cada 30 ms
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
        ], expand=True),
    ], expand=True)

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
card1 = ft.Card(content=ft.Text(""), expand=True)
card2 = ft.Card(content=ft.Text(""), expand=True)
card3 = ft.Card(content=ft.Text(""), expand=True)
service_history = HistoryService()
size_font = 9

try:
    model_path = os.path.join(os.path.dirname(__file__), "../model/runs/detect/train/weights/best.pt")
    model = YOLO(model_path)
except Exception as e:
    print(f"Error al cargar el modelo: {e}")
    exit()

folder_name_drivers = "drivers_images"
if not os.path.exists(folder_name_drivers):
    os.makedirs(folder_name_drivers)

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

def format_date(date):
    return date.strftime("%d/%m/%Y")

def get_hours(date):
    return date.strftime("%H:%M")

def generate_card(data):
    if data.authorized:
        file = os.path.join(folder_name_drivers, f"{data.vehicle.plate}_driver.jpg")
        print(file)
        if data.type == "Salida":
            color = ft.colors.REED_200
        else:
            color = ft.colors.GREEN_200
        return ft.Container(ft.Column([
            ft.Text(data.plate, size=30),
            ft.Container(
                content=Image(src_base64=data.image, width=200, height=150, fit=ft.ImageFit.CONTAIN,repeat=ft.ImageRepeat.NO_REPEAT),
                alignment=ft.alignment.center,
            ),
            ft.Row([
                ft.Text(f"Fecha: {format_date(data.created_at)}", size=size_font),
                ft.Text(f"Hora: {get_hours(data.created_at)}", size=size_font),
                ], spacing=1, alignment=ft.MainAxisAlignment.SPACE_BETWEEN )
            ,
            ft.Row([
                ft.Container(
                    content=Image(src=file, width=100, fit=ft.ImageFit.CONTAIN,repeat=ft.ImageRepeat.NO_REPEAT),
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
                content=Image(src_base64=data.image, width=200, height=150, fit=ft.ImageFit.CONTAIN,repeat=ft.ImageRepeat.NO_REPEAT),
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


def add_history(plate):
    history = service_history.create_history(plate, camera_feed.src_base64)
    if not history:
        return
    # Desplazar la información existente
    card3.content = card2.content
    card3.color = card2.color
    card2.content = card1.content
    card2.color = card1.color
    # Obtener la última historia agregada
    last_history = service_history.get_last_history()
    # Actualizar card1 con la nueva información
    if last_history.authorized:
        card1.color = ft.colors.GREEN_200
    else:
        card1.color = ft.colors.RED_200

    card1.content = generate_card(last_history)
    card1.update()
    card2.update()
    card3.update()
    rows = service_history.get_histories_today()
    list.controls = [ft.Card(ft.Container(content=ft.Column([ft.Text(f"Placa: {row.plate}", size=14) ,ft.Text(f"Fecha: {format_date(row.created_at)} - Hora: {get_hours(row.created_at)}", size=size_font), ft.Text(f"{row.type}", size=size_font)]),padding=10)) for row in rows[3:]]
    list.update()

def get_histories_today(page):
    rows = service_history.get_histories_today()
    # Mostrar las primeras 3 filas con imagen e información
    for i, row in enumerate(rows[:3]):
        if i == 0 and row.image is not None:
            card1.content = generate_card(row)
            if row.authorized:
                card1.color = ft.colors.GREEN_200
            else:
                card1.color = ft.colors.RED_200
        elif i == 1 and row.image is not None:
            card2.content = generate_card(row)
            if row.authorized:
                card2.color = ft.colors.GREEN_200
            else:
                card2.color = ft.colors.RED_200
        elif i == 2 and row.image is not None:
            card3.content = generate_card(row)
            if row.authorized:
                card3.color = ft.colors.GREEN_200
            else:
                card3.color = ft.colors.RED_200

    list.controls = [ft.Card(ft.Container(content=ft.Column([ft.Text(f"Placa: {row.plate}", size=14) ,ft.Text(f"Fecha: {format_date(row.created_at)} - Hora: {get_hours(row.created_at)}", size=size_font), ft.Text(f"{row.type}", size=size_font)]),padding=10)) for row in rows[3:]]
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
        ft.Row([
            ft.Column([
                ft.Row([
                    title,
                    ft.Card(
                        content=camera_feed,
                        height=size_image,
                        expand=True,
                    ),
                ],vertical_alignment= ft.CrossAxisAlignment.START),
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

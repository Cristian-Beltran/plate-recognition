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
camera_feed = Image(height=480, src=False)
list = ft.ListView(spacing=5, padding=10, auto_scroll=False, width=200 )
card1 = ft.Card(content=ft.Text(""), height=430)
card2 = ft.Card(content=ft.Text(""), height=430)
card3 = ft.Card(content=ft.Text(""), height=430)
service_history = HistoryService()
size_font = 11

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
        color = ft.colors.RED_600 if data.type == "Salida" else ft.colors.GREEN_600
        return ft.Container(
            content=ft.Column([
                ft.Container(content=ft.Text(f"{data.plate}", size=30, weight=ft.FontWeight.BOLD,  text_align=ft.TextAlign.CENTER), alignment=ft.alignment.center),
                # Imagen del vehículo
                ft.Container(
                    content=ft.Image(src_base64=data.image, width=200, height=150, fit=ft.ImageFit.CONTAIN, repeat=ft.ImageRepeat.NO_REPEAT),
                    alignment=ft.alignment.center,
                    border_radius=8,
                ),
                # Fecha y Hora en fila con fondo
                ft.Row([
                    ft.Container(
                        content=ft.Text(f"Fecha: {format_date(data.created_at)}", size=size_font),
                        padding=ft.padding.all(8),  # Ajuste aquí
                        bgcolor=ft.colors.GREY_600,
                        border_radius=5,
                    ),
                    ft.Container(
                        content=ft.Text(f"Hora: {get_hours(data.created_at)}", size=size_font),
                        padding=ft.padding.all(8),  # Ajuste aquí
                        bgcolor=ft.colors.GREY_600,
                        border_radius=5,
                    ),
                ], spacing=10, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

                # Información del conductor en fila con fondo
                ft.Row([
                    ft.Container(
                        content=ft.Image(src=file, width=70, fit=ft.ImageFit.CONTAIN, repeat=ft.ImageRepeat.NO_REPEAT),
                        alignment=ft.alignment.center,
                    ),
                    ft.Column([
                        ft.Container(
                            content=ft.Text(f"Marca: {data.vehicle.make}", size=size_font),
                            padding=ft.padding.all(6),  # Ajuste aquí
                            bgcolor=ft.colors.GREY_600,
                            border_radius=5,
                        ),
                        ft.Container(
                            content=ft.Text(f"Color: {data.vehicle.color}", size=size_font),
                            padding=ft.padding.all(6),  # Ajuste aquí
                            bgcolor=ft.colors.GREY_600,
                            border_radius=5,
                        ),
                        ft.Container(
                            content=ft.Text(f"Nombre: {data.vehicle.first_name} {data.vehicle.last_name}", size=size_font),
                            padding=ft.padding.all(6),  # Ajuste aquí
                            bgcolor=ft.colors.GREY_600,
                            border_radius=5,
                        ),
                    ], spacing=4)
                ]),

                # Personal, CI y tipo en fila
                ft.Row([
                    ft.Container(
                        content=ft.Text(f"Personal: {data.vehicle.personal}", size=size_font),
                        padding=ft.padding.all(8),  # Ajuste aquí
                        bgcolor=ft.colors.GREY_600,
                        border_radius=5,
                    ),
                    ft.Container(
                        content=ft.Text(f"CI: {data.vehicle.ci}", size=size_font),
                        padding=ft.padding.all(8),  # Ajuste aquí
                        bgcolor=ft.colors.GREY_600,
                        border_radius=5,
                    ),
                ], spacing=4, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Container(content=ft.Text(f"{data.type}", size=size_font, color=ft.colors.WHITE), padding=ft.padding.all(8), bgcolor=color, border_radius=5, alignment=ft.alignment.center),
            ], spacing=4),
            padding=10,
            bgcolor=ft.colors.GREY_800,
            border_radius=10,
            width=250,
            alignment=ft.alignment.center,
        )

    else:
        return ft.Container(
            content=ft.Column([
                ft.Container(content=ft.Text(f"{data.plate}", size=30, weight=ft.FontWeight.BOLD,  text_align=ft.TextAlign.CENTER), alignment=ft.alignment.center),
                # Imagen de no autorizada
                ft.Container(
                    content=ft.Image(src_base64=data.image, width=200, height=150, fit=ft.ImageFit.CONTAIN, repeat=ft.ImageRepeat.NO_REPEAT),
                    alignment=ft.alignment.center,
                    border_radius=8,
                ),

                # Fecha y Hora en fila con fondo
                ft.Row([
                    ft.Container(
                        content=ft.Text(f"Fecha: {format_date(data.created_at)}", size=size_font),
                        padding=ft.padding.all(8),  # Ajuste aquí
                        bgcolor=ft.colors.GREY_600,
                        border_radius=5,
                    ),
                    ft.Container(
                        content=ft.Text(f"Hora: {get_hours(data.created_at)}", size=size_font),
                        padding=ft.padding.all(8),  # Ajuste aquí
                        bgcolor=ft.colors.GREY_600,
                        border_radius=5,
                    ),
                ], spacing=10, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

                # Mensaje de no autorizado
                ft.Container(
                    content=ft.Text("NO AUTORIZADA", size=26, color=ft.colors.RED),
                    alignment=ft.alignment.center,
                    padding=ft.padding.all(10),  # Ajuste aquí
                    bgcolor=ft.colors.RED_50,
                    border_radius=8,
                ),
            ], spacing=4),
            padding=10,
            bgcolor=ft.colors.GREY_800,
            border_radius=10,
            width=250,
            alignment=ft.alignment.center,
            animate=ft.animation.Animation(1000, ft.AnimationCurve.BOUNCE_OUT),
        )

blink_thread = None
def blink_card(card, duration=60):
    global blink_thread
    def blink():
        end_time = time.time() + duration  # Duración de 60 segundos
        while time.time() < end_time:
            card.content.bgcolor = ft.colors.GREY_800 if card.content.bgcolor == ft.colors.RED_200 else ft.colors.RED_200
            card.update()  # Actualiza la tarjeta para reflejar el cambio de color
            time.sleep(0.5)  # Parpadea cada 0.5 segundos
        card.content.bgcolor = ft.colors.GREY_800
        card.update()
    if blink_thread is not None and blink_thread.is_alive():
        blink_thread.join(timeout=0)  # Espera a que el hilo actual termine

        # Iniciar un nuevo hilo de parpadeo
    blink_thread = threading.Thread(target=blink)
    blink_thread.start()

def add_history(plate):
    history = service_history.create_history(plate, camera_feed.src_base64)
    if not history:
        return
    rows = service_history.get_histories_today()
    for i, row in enumerate(rows[:3]):
        if i == 0 and row.image is not None:
            card1.content = generate_card(row)
            if (not row.authorized):
                print("Blinking")
                blink_card(card1)
        elif i == 1 and row.image is not None:
            card2.content = generate_card(row)
        elif i == 2 and row.image is not None:
            card3.content = generate_card(row)
    card1.update()
    card2.update()
    card3.update()
    list.controls = [ft.Card(ft.Container(content=ft.Column([ft.Text(f"Placa: {row.plate}", size=14) ,ft.Text(f"Fecha: {format_date(row.created_at)} - Hora: {get_hours(row.created_at)}", size=size_font), ft.Text(f"{row.type}", size=size_font)]),padding=10), color= (row.authorized and ft.colors.GREY_600 or ft.colors.RED_200)) for row in rows[3:]]
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

    list.controls = [ft.Card(ft.Container(content=ft.Column([ft.Text(f"Placa: {row.plate}", size=14) ,ft.Text(f"Fecha: {format_date(row.created_at)} - Hora: {get_hours(row.created_at)}", size=size_font), ft.Text(f"{row.type}", size=size_font)]),padding=10), color= (row.authorized and ft.colors.GREY_600 or ft.colors.RED_200)) for row in rows[3:]]
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
                                if filtered_text and len(text) < 8:
                                    add_history(text)
                                    cv2.putText(frame, text, (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
                # Actualizar el feed de la cámara en la interfaz
                _, img_encoded = cv2.imencode('.png', frame)
                img_base64 = base64.b64encode(img_encoded)
                camera_feed.src_base64 = img_base64.decode('utf-8')
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
        stop_event.clear()
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
                    ft.Container(content=card1),
                    ft.Container(content=card2),
                    ft.Container(content=card3),
                ], alignment=ft.MainAxisAlignment.CENTER)
            ], expand=True),
            ft.VerticalDivider(width=1),
            list,
        ], expand=True),
    ], expand=True)

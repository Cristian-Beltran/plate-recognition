
# Detección de Placas Vehiculares y Gestión de Estacionamiento

Este proyecto es una aplicación que permite gestionar las entradas y salidas de vehículos en el estacionamiento de un apartamento. Utiliza un modelo de IA (**YOLO**) para detectar las placas vehiculares y **Tesseract** para leer el texto de las placas. La aplicación está construida usando **Flet** para la interfaz gráfica y cuenta con las siguientes funcionalidades:

## Características

- **Detección de Placas Vehiculares:** Utiliza YOLO para detectar vehículos y extraer las placas.
- **Reconocimiento de Texto:** Emplea Tesseract para leer el texto de las placas vehiculares detectadas.
- **Registro de Vehículos:** Permite registrar vehículos en el sistema.
- **Gestión de Usuarios:** Permite gestionar usuarios del sistema con acceso al registro.
- **Historial de Entradas/Salidas:** Guarda un historial de todas las entradas de vehículos, indicando si fueron autorizadas o no.

## Requisitos

Para ejecutar esta aplicación, necesitas instalar las siguientes dependencias.

### Instalar dependencias de Python

Primero, asegúrate de tener `pip` y `virtualenv` instalados. Luego, sigue los pasos para instalar las dependencias:

1. Clona este repositorio:

    ```bash
    git clone https://github.com/Cristian-Beltran/plate-recognition
    cd plate-recognition
    ```

2. Crea un entorno virtual y actívalo:
    ```bash
    python -m venv venv
    source venv/bin/activate    # En Linux/macOS
    .\venv\Scripts\activate     # En Windows
    ```

3. Instala las dependencias del archivo `requirements.txt`:

    ```bash
    pip install -r requirements.txt
    ```

### Instalar Tesseract

El proyecto requiere que **Tesseract** esté instalado para realizar el reconocimiento de texto (OCR). Sigue las instrucciones a continuación según tu sistema operativo:

#### Windows

1. Descarga el instalador de Tesseract desde su [página oficial](https://github.com/UB-Mannheim/tesseract/wiki).
2. Durante la instalación, asegúrate de agregar Tesseract al **PATH**.
3. Verifica la instalación con:

    ```bash
    tesseract --version
    ```

#### Linux (Debian/Ubuntu)

1. Instala Tesseract desde los repositorios oficiales:

    ```bash
    sudo apt update
    sudo apt install tesseract-ocr
    ```

2. Verifica la instalación con:

    ```bash
    tesseract --version
    ```

#### macOS

1. Instala Tesseract usando Homebrew:

    ```bash
    brew install tesseract
    ```

2. Verifica la instalación con:

    ```bash
    tesseract --version
    ```

### YOLO (Ultralytics)

El modelo de detección de objetos se basa en **YOLO** (You Only Look Once). Asegúrate de tener configurado el modelo antes de ejecutar la aplicación.

1. Instala **ultralytics** para manejar el modelo de YOLO:

    ```bash
    pip install ultralytics
    ```

2. Si necesitas cargar un modelo preentrenado para la detección de placas, puedes descargar el modelo utilizando el siguiente comando en tu script:

    ```python
    from ultralytics import YOLO
    model = YOLO('ruta/al/modelo')
    ```
3. En este caso la aplicaion ya cuenta con un modelo preentrenado para la detección de placas.

## Ejecución
Después de instalar todas las dependencias y Tesseract, puedes ejecutar la aplicación con el siguiente comando:

```bash
flet run

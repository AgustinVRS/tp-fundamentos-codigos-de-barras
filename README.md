## Instalación y ejecución

Necesitás tener Python 3 instalado. Descargá el repositorio desde **Code → Download ZIP** y descomprimilo, o clonalo con Git. Abrí una terminal en la carpeta del proyecto, donde está `main.py`.

### Windows (PowerShell)

1. Creá un entorno virtual:

   ```powershell
   py -3 -m venv .venv
   ```

2. Instalá las dependencias con el Python del entorno:

   ```powershell
   .\.venv\Scripts\python.exe -m pip install customtkinter python-barcode Pillow
   ```

3. Abrí la aplicación:

   ```powershell
   .\.venv\Scripts\python.exe main.py
   ```

Si PowerShell no reconoce `py` pero sí `python`, usá `python -m venv .venv` en el primer paso.

### Linux (Debian, Ubuntu y derivados)

1. Instalá el soporte para entornos virtuales y Tkinter, que usa la interfaz gráfica:

   ```bash
   sudo apt update
   sudo apt install python3-venv python3-tk
   ```

2. Creá un entorno virtual:

   ```bash
   python3 -m venv .venv
   ```

3. Instalá las dependencias dentro del entorno:

   ```bash
   .venv/bin/python -m pip install customtkinter python-barcode Pillow
   ```

4. Abrí la aplicación desde una sesión con escritorio gráfico:

   ```bash
   .venv/bin/python main.py
   ```

### Para volver a abrir la aplicación

Desde la carpeta del proyecto, repetí solo el comando que ejecuta `main.py` para tu sistema. Las dependencias quedan instaladas en `.venv`.
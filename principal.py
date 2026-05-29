"""Punto de entrada del cliente. Ejecutar: python principal.py"""

import atexit
import logging
import time
import tkinter as tk
from threading import Thread
from urllib.error import URLError
from urllib.request import urlopen

from cliente.aplicacion import AplicacionTransporte
from nucleo import config_tarifas

API_STATUS_URL = "http://127.0.0.1:5000/status"
API_START_TIMEOUT = 8
api_servidor = None
api_hilo = None


def api_esta_activa():
    try:
        with urlopen(API_STATUS_URL, timeout=0.8) as respuesta:
            return respuesta.status == 200
    except (OSError, TimeoutError, URLError):
        return False


def iniciar_api_si_hace_falta():
    global api_servidor, api_hilo
    if api_esta_activa():
        return

    from servidor.app import app
    from werkzeug.serving import make_server

    try:
        api_servidor = make_server("127.0.0.1", 5000, app)
    except OSError as error:
        print(f"No se pudo iniciar la API en 127.0.0.1:5000: {error}")
        api_servidor = None
        return

    logging.getLogger("werkzeug").setLevel(logging.ERROR)
    api_hilo = Thread(target=api_servidor.serve_forever, name="api-flask", daemon=True)
    api_hilo.start()

    limite = time.time() + API_START_TIMEOUT
    while time.time() < limite:
        if api_esta_activa():
            return
        time.sleep(0.25)


def cerrar_api_iniciada():
    global api_servidor, api_hilo
    if api_servidor is None:
        return
    api_servidor.shutdown()
    if api_hilo is not None:
        api_hilo.join(timeout=3)
    api_servidor = None
    api_hilo = None


def abrir_cliente():
    config_tarifas.obtener()
    iniciar_api_si_hace_falta()
    atexit.register(cerrar_api_iniciada)

    root = tk.Tk()
    root.protocol("WM_DELETE_WINDOW", lambda: (cerrar_api_iniciada(), root.destroy()))
    AplicacionTransporte(root)
    root.mainloop()


if __name__ == "__main__":
    abrir_cliente()

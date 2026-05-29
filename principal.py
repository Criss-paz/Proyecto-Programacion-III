"""Punto de entrada del cliente. Ejecutar: python principal.py"""

import tkinter as tk
from nucleo import config_tarifas
<<<<<<< HEAD

API_STATUS_URL = "http://127.0.0.1:5000/status"
API_START_TIMEOUT = 8
api_proceso = None


def api_esta_activa():
    try:
        with urlopen(API_STATUS_URL, timeout=0.8) as respuesta:
            return respuesta.status == 200
    except (OSError, TimeoutError, URLError):
        return False


def iniciar_api_si_hace_falta():
    global api_proceso
    if api_esta_activa():
        return

    raiz = Path(__file__).resolve().parent
    opciones = {"cwd": raiz, "stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL}
    if sys.platform.startswith("win"):
        opciones["creationflags"] = subprocess.CREATE_NO_WINDOW

    api_proceso = subprocess.Popen([sys.executable, str(raiz / "api.py")], **opciones)
    limite = time.time() + API_START_TIMEOUT
    while time.time() < limite:
        if api_esta_activa() or api_proceso.poll() is not None:
            return
        time.sleep(0.25)


def cerrar_api_iniciada():
    if api_proceso is None or api_proceso.poll() is not None:
        return
    api_proceso.terminate()
    try:
        api_proceso.wait(timeout=3)
    except subprocess.TimeoutExpired:
        api_proceso.kill()


def abrir_cliente():
    config_tarifas.obtener()
    iniciar_api_si_hace_falta()
    atexit.register(cerrar_api_iniciada)

    root = tk.Tk()
    root.protocol("WM_DELETE_WINDOW", lambda: (cerrar_api_iniciada(), root.destroy()))
=======
from cliente.aplicacion import AplicacionTransporte

if __name__ == "__main__":
    config_tarifas.obtener()
    root = tk.Tk()
>>>>>>> parent of 67c534d (Actualizacion API)
    AplicacionTransporte(root)
    root.mainloop()


if __name__ == "__main__":
    abrir_cliente()

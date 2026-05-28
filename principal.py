"""
Punto de entrada del CLIENTE.
Ejecutar: python principal.py
"""

import tkinter as tk
from nucleo import config_tarifas
from cliente.aplicacion import AplicacionTransporte

if __name__ == "__main__":
    config_tarifas.obtener()
    root = tk.Tk()
    AplicacionTransporte(root)
    root.mainloop()

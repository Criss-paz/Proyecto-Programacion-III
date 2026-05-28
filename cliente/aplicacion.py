"""
Ventana principal del cliente.
Conecta con la API, cambia de pestaña y delega a Cotizador / Administrador.
"""

import tkinter as tk
from tkinter import ttk
import numpy as np
import requests
from cliente.ui_helpers import (
    API_URL, COLOR_FONDO, COLOR_PANEL, COLOR_BORDE, COLOR_TEXTO, COLOR_SUAVE,
    COLOR_PRIMARIO, COLOR_ERROR, COLOR_EXITO, UIHelpers,
)
from cliente.vista_cotizador import VistaCotizador
from cliente.vista_admin import VistaAdmin


class AplicacionTransporte(VistaCotizador, VistaAdmin, UIHelpers):
    def __init__(self, root):
        self.root = root
        self.root.title("Envios Rapidos GT")
        self.root.geometry("1180x720")
        self.root.minsize(980, 640)
        self.root.configure(bg=COLOR_FONDO)

        self.municipios, self.matriz = [], None
        self.api_conectada, self.ruta_actual = False, []
        self.zoom_grafo, self.desplazamiento_grafo = 1.0, (0.0, 0.0)

        estilo = ttk.Style()
        estilo.theme_use("clam")
        estilo.configure("TCombobox", padding=7, font=("Segoe UI", 10))
        estilo.configure("TEntry", padding=7, font=("Segoe UI", 10))

        self._crear_encabezado()
        self.contenido = tk.Frame(self.root, bg=COLOR_FONDO)
        self.contenido.pack(fill="both", expand=True, padx=22, pady=20)
        self.reconectar_api()

    def _crear_encabezado(self):
        enc = tk.Frame(self.root, bg=COLOR_PANEL, highlightbackground=COLOR_BORDE, highlightthickness=1)
        enc.pack(fill="x")
        info = tk.Frame(enc, bg=COLOR_PANEL)
        info.pack(side="left", padx=24, pady=16)
        tk.Label(info, text="Envios Rapidos GT", bg=COLOR_PANEL, fg=COLOR_TEXTO, font=("Segoe UI", 18, "bold")).pack(side="left")
        self.lbl_status_api = tk.Label(info, text="API: Conectando...", bg="#f1f5f9", fg=COLOR_SUAVE, font=("Segoe UI", 9, "bold"), padx=10, pady=3)
        self.lbl_status_api.pack(side="left", padx=15)

        nav = tk.Frame(enc, bg=COLOR_PANEL)
        nav.pack(side="right", padx=18)
        self.btn_cotizador = self._boton(nav, "Cotizador", lambda: self.cambiar_pestana("cotizador"), primario=True)
        self.btn_admin = self._boton(nav, "Administrador", lambda: self.cambiar_pestana("admin"))
        self.btn_cotizador.pack(side="left", padx=5)
        self.btn_admin.pack(side="left", padx=5)

    def cambiar_pestana(self, vista):
        self.vista_actual = vista
        for btn, nombre in ((self.btn_cotizador, "cotizador"), (self.btn_admin, "admin")):
            activo = vista == nombre
            btn.configure(bg=COLOR_PRIMARIO if activo else "#e2e8f0", fg="#ffffff" if activo else COLOR_TEXTO)
        self.refrescar_vista()

    def refrescar_vista(self):
        for w in self.contenido.winfo_children():
            w.destroy()
        if not self.api_conectada:
            self._pantalla_error()
        elif self.vista_actual == "cotizador":
            self.mostrar_cotizador()
        else:
            self.mostrar_administrador()

    def _api(self, ruta, params=None, timeout=2.0):
        return requests.get(f"{API_URL}{ruta}", params=params, timeout=timeout).json()

    def reconectar_api(self):
        self.lbl_status_api.config(text="API: Conectando...", fg=COLOR_SUAVE, bg="#f1f5f9")
        self.root.update_idletasks()
        try:
            res = self._api("/datos")
            self.municipios, self.matriz = res["municipios"], np.array(res["matriz"])
            self.api_conectada = True
            self.lbl_status_api.config(text="API: Conectada", fg="#ffffff", bg=COLOR_EXITO)
        except Exception:
            self.municipios, self.matriz, self.api_conectada = [], None, False
            self.lbl_status_api.config(text="API: Desconectada", fg="#ffffff", bg=COLOR_ERROR)
        if not hasattr(self, "vista_actual"):
            self.vista_actual = "cotizador"
        self.cambiar_pestana(self.vista_actual)

    def _pantalla_error(self):
        err = tk.Frame(self.contenido, bg=COLOR_PANEL, highlightbackground=COLOR_BORDE, highlightthickness=1)
        err.pack(fill="both", expand=True, padx=40, pady=40)
        tk.Label(err, text="Servidor API fuera de línea", bg=COLOR_PANEL, fg=COLOR_ERROR, font=("Segoe UI", 20, "bold")).pack(pady=(60, 10))
        tk.Label(err, text=f"No se pudo conectar con {API_URL}.\nEjecuta 'python api.py' primero.", bg=COLOR_PANEL, fg=COLOR_TEXTO, font=("Segoe UI", 11), justify="center").pack(pady=10)
        self._boton(err, "🔄 Intentar Reconectar", self.reconectar_api, primario=True).pack(pady=20)

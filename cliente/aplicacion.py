"""Ventana principal del cliente."""

import tkinter as tk
from tkinter import ttk

import numpy as np
import requests

from cliente.ui_helpers import (
    API_URL, COLOR_BORDE, COLOR_ERROR, COLOR_EXITO, COLOR_FONDO, COLOR_PANEL,
    COLOR_PRIMARIO, COLOR_SUAVE, COLOR_TEXTO, UIHelpers,
)
from cliente.vista_admin import VistaAdmin
from cliente.vista_cotizador import VistaCotizador


class AplicacionTransporte(VistaCotizador, VistaAdmin, UIHelpers):
    def __init__(self, root, conectar_al_inicio=True):
        self.root = root
        self.root.title("Envios Rapidos GT")
        self.root.geometry("1180x720")
        self.root.minsize(980, 640)
        self.root.configure(bg=COLOR_FONDO)

        self.municipios, self.matriz = [], None
        self.api_conectada, self.ruta_actual = False, []
        self.conectando_api = not conectar_al_inicio
        self.zoom_grafo, self.desplazamiento_grafo = 1.0, (0.0, 0.0)

        estilo = ttk.Style()
        estilo.theme_use("clam")
        estilo.configure("TCombobox", padding=7, font=("Segoe UI", 10))
        estilo.configure("TEntry", padding=7, font=("Segoe UI", 10))

        self._crear_encabezado()
        self.contenido = tk.Frame(self.root, bg=COLOR_FONDO)
        self.contenido.pack(fill="both", expand=True, padx=22, pady=20)
        if conectar_al_inicio:
            self.reconectar_api()
        else:
            self.vista_actual = "cotizador"
            self.refrescar_vista()

    def _crear_encabezado(self):
        encabezado = tk.Frame(self.root, bg=COLOR_PANEL, highlightbackground=COLOR_BORDE, highlightthickness=1)
        encabezado.pack(fill="x")

        info = tk.Frame(encabezado, bg=COLOR_PANEL)
        info.pack(side="left", padx=24, pady=16)
        self._crear_logo(info)
        self._label(info, "Envios Rapidos GT", 18, True, COLOR_TEXTO, side="left")
        self.lbl_status_api = tk.Label(info, text="API: Conectando...", bg="#f1f5f9",
                                       fg=COLOR_SUAVE, font=("Segoe UI", 9, "bold"), padx=10, pady=3)
        self.lbl_status_api.pack(side="left", padx=15)

        nav = tk.Frame(encabezado, bg=COLOR_PANEL)
        nav.pack(side="right", padx=18)
        self.btn_cotizador = self._boton(nav, "Cotizador", lambda: self.cambiar_pestana("cotizador"), True)
        self.btn_admin = self._boton(nav, "Administrador", lambda: self.cambiar_pestana("admin"))
        self.btn_cotizador.pack(side="left", padx=5)
        self.btn_admin.pack(side="left", padx=5)

    def _crear_logo(self, parent):
        logo = tk.Canvas(parent, width=46, height=46, bg=COLOR_PANEL, highlightthickness=0)
        logo.pack(side="left", padx=(0, 12))
        logo.create_oval(3, 3, 43, 43, fill=COLOR_PRIMARIO, outline="")
        logo.create_polygon(13, 14, 34, 23, 13, 32, 18, 24, fill="#ffffff", outline="")
        logo.create_line(19, 23, 34, 23, fill=COLOR_PANEL, width=2)

    def cambiar_pestana(self, vista):
        self.vista_actual = vista
        for boton, nombre in ((self.btn_cotizador, "cotizador"), (self.btn_admin, "admin")):
            activo = vista == nombre
            boton.configure(bg=COLOR_PRIMARIO if activo else "#e2e8f0", fg="#ffffff" if activo else COLOR_TEXTO)
        self.refrescar_vista()

    def refrescar_vista(self):
        for widget in self.contenido.winfo_children():
            widget.destroy()
        if not self.api_conectada and self.conectando_api:
            self._pantalla_conectando()
        elif not self.api_conectada:
            self._pantalla_error()
        elif self.vista_actual == "cotizador":
            self.mostrar_cotizador()
        else:
            self.mostrar_administrador()

    def _api(self, ruta, params=None, timeout=2.0):
        respuesta = requests.get(f"{API_URL}{ruta}", params=params, timeout=timeout)
        respuesta.raise_for_status()
        return respuesta.json()

    def reconectar_api(self):
        self.conectando_api = True
        self._estado_api("API: Conectando...", COLOR_SUAVE, "#f1f5f9")
        try:
            datos = self._api("/datos")
            self.municipios, self.matriz = datos["municipios"], np.array(datos["matriz"])
            self.api_conectada = True
            self._estado_api("API: Conectada", "#ffffff", COLOR_EXITO)
        except Exception:
            self.municipios, self.matriz, self.api_conectada = [], None, False
            self._estado_api("API: Desconectada", "#ffffff", COLOR_ERROR)

        self.conectando_api = False
        if not hasattr(self, "vista_actual"):
            self.vista_actual = "cotizador"
        self.cambiar_pestana(self.vista_actual)

    def _estado_api(self, texto, fg, bg):
        self.lbl_status_api.config(text=texto, fg=fg, bg=bg)
        self.root.update_idletasks()

    def _pantalla_error(self):
        panel = tk.Frame(self.contenido, bg=COLOR_PANEL, highlightbackground=COLOR_BORDE, highlightthickness=1)
        panel.pack(fill="both", expand=True, padx=40, pady=40)
        self._label(panel, "Servidor API fuera de linea", 20, True, COLOR_ERROR, pady=(60, 10))
        self._label(panel, f"No se pudo conectar con {API_URL}.\nLa app intento iniciar la API automaticamente.",
                    11, color=COLOR_TEXTO, pady=10)
        self._boton(panel, "Intentar Reconectar", self.reconectar_api, primario=True).pack(pady=20)

    def _pantalla_conectando(self):
        panel = tk.Frame(self.contenido, bg=COLOR_PANEL, highlightbackground=COLOR_BORDE, highlightthickness=1)
        panel.pack(fill="both", expand=True, padx=40, pady=40)
        self._label(panel, "Iniciando aplicacion...", 20, True, COLOR_TEXTO, pady=(80, 10))
        self._label(panel, "Preparando la API y cargando los datos.", 11, color=COLOR_TEXTO, pady=10)

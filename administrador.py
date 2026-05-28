# administrador.py
import tkinter as tk
from tkinter import ttk
import lector_excel
from cliente_ui import VistaCajero, VistaAdministrador

class ControlPestanas:
    """Clase que unifica las pantallas en un menu navegable con pestanas."""
    def __init__(self, root):
        self.root = root
        self.root.title("GT-EXPRESS S.A. - Sistema Integral de Control")
        self.root.geometry("520x660")
        
        # Cargar municipios reales del Excel
        try:
            municipios, _ = lector_excel.cargar_datos()
        except Exception:
            municipios = []

        # Crear panel de pestanas
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True)

        # Unificar las vistas de cliente_ui.py (Variables sin tildes)
        self.pestana_caja = VistaCajero(self.notebook, municipios)
        self.pestana_admin = VistaAdministrador(self.notebook)

        self.notebook.add(self.pestana_caja, text=" Cotizador de Envios ")
        self.notebook.add(self.pestana_admin, text=" Panel de Auditoria ")

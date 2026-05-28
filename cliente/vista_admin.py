"""Pantalla Administrador: estado de la API y edición de tarifas."""

import tkinter as tk
from tkinter import messagebox, ttk
from nucleo import config_tarifas
from cliente.ui_helpers import COLOR_PANEL, COLOR_TEXTO, COLOR_SUAVE, COLOR_BORDE


class VistaAdmin:
    def mostrar_administrador(self):
        panel = tk.Frame(self.contenido, bg=COLOR_PANEL, highlightbackground=COLOR_BORDE, highlightthickness=1)
        panel.pack(fill="both", expand=True)
        self._titulo(panel, "Administrador", "Estado de la API y configuración de tarifas.")

        resumen = tk.Frame(panel, bg=COLOR_PANEL)
        resumen.pack(fill="x", padx=18, pady=10)
        for c in range(3):
            resumen.columnconfigure(c, weight=1)

        dim = f"{self.matriz.shape[0]} x {self.matriz.shape[1]}" if self.matriz is not None else "Sin datos"
        self._indicador(resumen, "Municipios", len(self.municipios), 0)
        self._indicador(resumen, "Matriz", dim, 1)
        self._indicador(resumen, "Estado API", "Conectada", 2)

        acciones = tk.Frame(panel, bg=COLOR_PANEL)
        acciones.pack(fill="x", padx=20, pady=(6, 12))
        self._boton(acciones, "Verificar Conexión", self.reconectar_api, primario=True).pack(side="left")

        cuerpo = tk.Frame(panel, bg=COLOR_PANEL)
        cuerpo.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        cuerpo.columnconfigure(0, weight=1, uniform="ad_col")
        cuerpo.columnconfigure(1, weight=1, uniform="ad_col")
        cuerpo.rowconfigure(0, weight=1)

        self._lista_municipios(cuerpo)
        self._formulario_tarifas(cuerpo)

    def _lista_municipios(self, cuerpo):
        col = tk.Frame(cuerpo, bg=COLOR_PANEL)
        col.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        tk.Label(col, text="Municipios Registrados", bg=COLOR_PANEL, fg=COLOR_TEXTO, font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 6))

        frame = tk.Frame(col, bg=COLOR_PANEL)
        frame.pack(fill="both", expand=True)
        scroll = ttk.Scrollbar(frame, orient="vertical")
        self.lista_admin = tk.Listbox(
            frame, bg="#f8fafc", fg=COLOR_TEXTO, highlightbackground=COLOR_BORDE,
            highlightthickness=1, bd=0, font=("Segoe UI", 10), yscrollcommand=scroll.set,
        )
        scroll.config(command=self.lista_admin.yview)
        scroll.pack(side="right", fill="y")
        self.lista_admin.pack(side="left", fill="both", expand=True)
        for i, m in enumerate(self.municipios, start=1):
            self.lista_admin.insert(tk.END, f"{i}. {m}")

    def _formulario_tarifas(self, cuerpo):
        col = tk.Frame(cuerpo, bg=COLOR_PANEL, highlightbackground=COLOR_BORDE, highlightthickness=1)
        col.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        tk.Label(col, text="Configuración de Tarifas", bg=COLOR_PANEL, fg=COLOR_TEXTO, font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=20, pady=(18, 4))
        tk.Label(col, text="Archivo único: nucleo/config_tarifas.py", bg=COLOR_PANEL, fg=COLOR_SUAVE, font=("Segoe UI", 9)).pack(anchor="w", padx=20, pady=(0, 14))

        config = config_tarifas.obtener()
        campos = [
            ("entry_c_base", "Costo Fijo Base (Q):", "COSTO_BASE"),
            ("entry_c_km", "Costo por Kilómetro (Q):", "COSTO_POR_KM"),
            ("entry_c_lb", "Costo por Libra (Q):", "COSTO_POR_LIBRA"),
            ("entry_utilidad", "Margen de Utilidad (0.0 - 0.99):", "MARGEN_UTILIDAD"),
        ]
        for attr, etiqueta, clave in campos:
            setattr(self, attr, self._entrada_tarifa(col, etiqueta, config[clave]))

        self._boton(col, "💾 Guardar Configuración", self.guardar_configuracion_ui, primario=True).pack(anchor="w", padx=20, pady=16)

    def _entrada_tarifa(self, parent, etiqueta, valor):
        frame = tk.Frame(parent, bg=COLOR_PANEL)
        frame.pack(fill="x", padx=20, pady=5)
        tk.Label(frame, text=etiqueta, bg=COLOR_PANEL, fg=COLOR_TEXTO, font=("Segoe UI", 9, "bold")).pack(anchor="w")
        entry = ttk.Entry(frame)
        entry.insert(0, f"{valor:.2f}" if isinstance(valor, float) else str(valor))
        entry.pack(fill="x", pady=2)
        return entry

    def guardar_configuracion_ui(self):
        try:
            val = {k: float(getattr(self, f"entry_{s}").get()) for k, s in [
                ("COSTO_BASE", "c_base"), ("COSTO_POR_KM", "c_km"),
                ("COSTO_POR_LIBRA", "c_lb"), ("MARGEN_UTILIDAD", "utilidad"),
            ]}
            if not 0.0 <= val["MARGEN_UTILIDAD"] < 1.0:
                raise ValueError("El margen de utilidad debe estar entre 0.0 y 0.99")
            if any(val[k] < 0 for k in ("COSTO_BASE", "COSTO_POR_KM", "COSTO_POR_LIBRA")):
                raise ValueError("Los costos no pueden ser negativos")
            if not config_tarifas.guardar(val):
                raise OSError("Error al escribir nucleo/config_tarifas.py.")
            messagebox.showinfo("Éxito", "Tarifas guardadas en nucleo/config_tarifas.py.")
            self.mostrar_administrador()
        except Exception as e:
            messagebox.showerror("Error", f"Ingresa valores válidos.\nDetalle: {e}")

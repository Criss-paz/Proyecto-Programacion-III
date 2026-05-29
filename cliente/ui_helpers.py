"""Colores, URL de la API y widgets reutilizables."""

import tkinter as tk
from tkinter import ttk

API_URL = "http://127.0.0.1:5000"
FUENTE = "Segoe UI"

COLOR_FONDO = "#f8fafc"
COLOR_PANEL = "#ffffff"
COLOR_BORDE = "#e2e8f0"
COLOR_TEXTO = "#0f172a"
COLOR_SUAVE = "#64748b"
COLOR_PRIMARIO = "#2563eb"
COLOR_PRIMARIO_HOVER = "#1d4ed8"
COLOR_ERROR = "#ef4444"
COLOR_EXITO = "#22c55e"


class ScrollableFrame(tk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.configure(bg=COLOR_PANEL)

        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0, bg=COLOR_PANEL)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=COLOR_PANEL)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.scrollable_frame.bind("<Configure>", self._actualizar_scroll)
        self.canvas.bind("<Configure>", self._ajustar_ancho)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.bind("<Enter>", lambda event: self.canvas.bind_all("<MouseWheel>", self._mover_scroll))
        self.canvas.bind("<Leave>", lambda event: self.canvas.unbind_all("<MouseWheel>"))

    def _actualizar_scroll(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _ajustar_ancho(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _mover_scroll(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


class UIHelpers:
    def _label(self, parent, texto, size=10, bold=False, color=COLOR_TEXTO, **pack_options):
        label = tk.Label(
            parent, text=texto, bg=COLOR_PANEL, fg=color,
            font=(FUENTE, size, "bold" if bold else "normal"),
        )
        label.pack(**pack_options)
        return label

    def _panel(self, parent, **grid_options):
        panel = tk.Frame(parent, bg=COLOR_PANEL, highlightbackground=COLOR_BORDE, highlightthickness=1)
        panel.grid(**grid_options)
        return panel

    def _titulo(self, parent, texto, ayuda=None):
        self._label(parent, texto, 16, True, anchor="w", padx=20, pady=(18, 2))
        if ayuda:
            self._label(parent, ayuda, color=COLOR_SUAVE, anchor="w", padx=20, pady=(0, 12))

    def _campo(self, parent, etiqueta, widget):
        self._label(parent, etiqueta, bold=True, anchor="w", padx=20, pady=(9, 4))
        widget.pack(fill="x", padx=20)

    def _boton(self, parent, texto, comando, primario=False):
        return tk.Button(
            parent,
            text=texto,
            command=comando,
            relief="flat",
            bd=0,
            padx=14,
            pady=9,
            cursor="hand2",
            font=(FUENTE, 10, "bold"),
            bg=COLOR_PRIMARIO if primario else "#e2e8f0",
            fg="#ffffff" if primario else COLOR_TEXTO,
            activebackground=COLOR_PRIMARIO_HOVER if primario else "#cbd5e1",
            activeforeground="#ffffff" if primario else COLOR_TEXTO,
        )

    def _resultado(self, parent, titulo, valor, color_resaltado=None, grande=False):
        self._label(parent, titulo, 9, True, COLOR_SUAVE, anchor="w", padx=20, pady=(8, 0))
        label = tk.Label(
            parent,
            text=valor,
            bg=COLOR_PANEL,
            fg=color_resaltado or COLOR_TEXTO,
            justify="left",
            wraplength=280,
            font=(FUENTE, 15 if grande else 10, "bold" if (grande or color_resaltado) else "normal"),
        )
        label.pack(anchor="w", padx=20, pady=(2, 4))
        return label

    def _indicador(self, parent, titulo, valor, columna):
        caja = tk.Frame(parent, bg="#f8fafc", highlightbackground=COLOR_BORDE, highlightthickness=1)
        caja.grid(row=0, column=columna, sticky="ew", padx=5, ipady=11)
        tk.Label(caja, text=titulo, bg="#f8fafc", fg=COLOR_SUAVE, font=(FUENTE, 9, "bold")).pack()
        tk.Label(caja, text=str(valor), bg="#f8fafc", fg=COLOR_TEXTO, font=(FUENTE, 14, "bold")).pack()

"""Colores, URL de la API y widgets reutilizables de la interfaz."""

import tkinter as tk
from tkinter import ttk

COLOR_FONDO, COLOR_PANEL, COLOR_BORDE = "#f8fafc", "#ffffff", "#e2e8f0"
COLOR_TEXTO, COLOR_SUAVE = "#0f172a", "#64748b"
COLOR_PRIMARIO, COLOR_PRIMARIO_HOVER = "#2563eb", "#1d4ed8"
COLOR_ERROR, COLOR_EXITO = "#ef4444", "#22c55e"
API_URL = "http://localhost:5000"
FUENTE = "Segoe UI"


class ScrollableFrame(tk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.configure(bg=COLOR_PANEL)
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0, bg=COLOR_PANEL)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=COLOR_PANEL)
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.bind("<Enter>", lambda e: self.canvas.bind_all("<MouseWheel>", self._on_mousewheel))
        self.canvas.bind("<Leave>", lambda e: self.canvas.unbind_all("<MouseWheel>"))

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


class UIHelpers:
    def _panel(self, parent, **grid_options):
        panel = tk.Frame(parent, bg=COLOR_PANEL, highlightbackground=COLOR_BORDE, highlightthickness=1)
        panel.grid(**grid_options)
        return panel

    def _titulo(self, parent, texto, ayuda=None):
        tk.Label(parent, text=texto, bg=COLOR_PANEL, fg=COLOR_TEXTO, font=(FUENTE, 16, "bold")).pack(anchor="w", padx=20, pady=(18, 2))
        if ayuda:
            tk.Label(parent, text=ayuda, bg=COLOR_PANEL, fg=COLOR_SUAVE, font=(FUENTE, 10)).pack(anchor="w", padx=20, pady=(0, 12))

    def _campo(self, parent, etiqueta, widget):
        tk.Label(parent, text=etiqueta, bg=COLOR_PANEL, fg=COLOR_TEXTO, font=(FUENTE, 10, "bold")).pack(anchor="w", padx=20, pady=(9, 4))
        widget.pack(fill="x", padx=20)

    def _boton(self, parent, texto, comando, primario=False):
        return tk.Button(
            parent, text=texto, command=comando, relief="flat", bd=0, padx=14, pady=9, cursor="hand2",
            font=(FUENTE, 10, "bold"), bg=COLOR_PRIMARIO if primario else "#e2e8f0",
            fg="#ffffff" if primario else COLOR_TEXTO,
            activebackground=COLOR_PRIMARIO_HOVER if primario else "#cbd5e1",
            activeforeground="#ffffff" if primario else COLOR_TEXTO,
        )

    def _resultado(self, parent, titulo, valor, color_resaltado=None, grande=False):
        tk.Label(parent, text=titulo, bg=COLOR_PANEL, fg=COLOR_SUAVE, font=(FUENTE, 9, "bold")).pack(anchor="w", padx=20, pady=(8, 0))
        lbl = tk.Label(
            parent, text=valor, bg=COLOR_PANEL, fg=color_resaltado or COLOR_TEXTO, justify="left", wraplength=280,
            font=(FUENTE, 15 if grande else 10, "bold" if (grande or color_resaltado) else "normal"),
        )
        lbl.pack(anchor="w", padx=20, pady=(2, 4))
        return lbl

    def _indicador(self, parent, titulo, valor, columna):
        caja = tk.Frame(parent, bg="#f8fafc", highlightbackground=COLOR_BORDE, highlightthickness=1)
        caja.grid(row=0, column=columna, sticky="ew", padx=5, ipady=11)
        tk.Label(caja, text=titulo, bg="#f8fafc", fg=COLOR_SUAVE, font=(FUENTE, 9, "bold")).pack()
        tk.Label(caja, text=str(valor), bg="#f8fafc", fg=COLOR_TEXTO, font=(FUENTE, 14, "bold")).pack()

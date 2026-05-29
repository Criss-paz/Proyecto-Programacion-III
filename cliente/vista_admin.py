"""Pantalla Administrador: estado de API y tarifas."""

import tkinter as tk
from tkinter import messagebox, ttk

from cliente.ui_helpers import COLOR_BORDE, COLOR_PANEL, COLOR_SUAVE, COLOR_TEXTO
from nucleo import config_tarifas


class VistaAdmin:
    CAMPOS_TARIFA = [
        ("entry_c_base", "Costo Fijo Base (Q):", "COSTO_BASE"),
        ("entry_c_km", "Costo por Kilometro (Q):", "COSTO_POR_KM"),
        ("entry_c_lb", "Costo por Libra (Q):", "COSTO_POR_LIBRA"),
        ("entry_utilidad", "Margen de Utilidad (0.0 - 0.99):", "MARGEN_UTILIDAD"),
    ]

    def mostrar_administrador(self):
        panel = tk.Frame(self.contenido, bg=COLOR_PANEL, highlightbackground=COLOR_BORDE, highlightthickness=1)
        panel.pack(fill="both", expand=True)
        self._titulo(panel, "Administrador", "Estado de la API y configuracion de tarifas.")
        self._resumen_api(panel)
        acciones = tk.Frame(panel, bg=COLOR_PANEL)
        acciones.pack(anchor="w", padx=20, pady=(6, 12))
        self._boton(acciones, "Verificar Conexion", self.reconectar_api, primario=True).pack(side="left")
        self._boton(acciones, "Ver Matriz Floyd", self.mostrar_matriz_floyd).pack(side="left", padx=8)

        cuerpo = tk.Frame(panel, bg=COLOR_PANEL)
        cuerpo.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        for col in range(2):
            cuerpo.columnconfigure(col, weight=1, uniform="admin")
        cuerpo.rowconfigure(0, weight=1)
        self._lista_municipios(cuerpo)
        self._formulario_tarifas(cuerpo)

    def _resumen_api(self, panel):
        resumen = tk.Frame(panel, bg=COLOR_PANEL)
        resumen.pack(fill="x", padx=18, pady=10)
        for col in range(3):
            resumen.columnconfigure(col, weight=1)
        dim = f"{self.matriz.shape[0]} x {self.matriz.shape[1]}" if self.matriz is not None else "Sin datos"
        for col, (titulo, valor) in enumerate([
            ("Municipios", len(self.municipios)),
            ("Matriz", dim),
            ("Estado API", "Conectada"),
        ]):
            self._indicador(resumen, titulo, valor, col)

    def _lista_municipios(self, cuerpo):
        col = tk.Frame(cuerpo, bg=COLOR_PANEL)
        col.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self._label(col, "Municipios Registrados", 11, True, anchor="w", pady=(0, 6))

        frame = tk.Frame(col, bg=COLOR_PANEL)
        frame.pack(fill="both", expand=True)
        scroll = ttk.Scrollbar(frame, orient="vertical")
        lista = tk.Listbox(frame, bg="#f8fafc", fg=COLOR_TEXTO, highlightbackground=COLOR_BORDE,
                           highlightthickness=1, bd=0, font=("Segoe UI", 10), yscrollcommand=scroll.set)
        scroll.config(command=lista.yview)
        scroll.pack(side="right", fill="y")
        lista.pack(side="left", fill="both", expand=True)
        for i, municipio in enumerate(self.municipios, start=1):
            lista.insert(tk.END, f"{i}. {municipio}")

    def _formulario_tarifas(self, cuerpo):
        col = tk.Frame(cuerpo, bg=COLOR_PANEL, highlightbackground=COLOR_BORDE, highlightthickness=1)
        col.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        self._label(col, "Configuracion de Tarifas", 13, True, anchor="w", padx=20, pady=(18, 4))
        self._label(col, "Archivo unico: nucleo/config_tarifas.py", 9, color=COLOR_SUAVE,
                    anchor="w", padx=20, pady=(0, 14))

        config = config_tarifas.obtener()
        for atributo, etiqueta, clave in self.CAMPOS_TARIFA:
            setattr(self, atributo, self._entrada_tarifa(col, etiqueta, config[clave]))
        self._boton(col, "Guardar Configuracion", self.guardar_configuracion_ui, primario=True).pack(
            anchor="w", padx=20, pady=16
        )

    def _entrada_tarifa(self, parent, etiqueta, valor):
        frame = tk.Frame(parent, bg=COLOR_PANEL)
        frame.pack(fill="x", padx=20, pady=5)
        self._label(frame, etiqueta, 9, True, anchor="w")
        entry = ttk.Entry(frame)
        entry.insert(0, f"{valor:.2f}")
        entry.pack(fill="x", pady=2)
        return entry

    def guardar_configuracion_ui(self):
        try:
            valores = {clave: float(getattr(self, atributo).get()) for atributo, _, clave in self.CAMPOS_TARIFA}
            if not 0 <= valores["MARGEN_UTILIDAD"] < 1:
                raise ValueError("El margen debe estar entre 0.0 y 0.99.")
            if any(valores[k] < 0 for k in ("COSTO_BASE", "COSTO_POR_KM", "COSTO_POR_LIBRA")):
                raise ValueError("Los costos no pueden ser negativos.")
            if not config_tarifas.guardar(valores):
                raise OSError("No se pudo escribir nucleo/config_tarifas.py.")
        except Exception as e:
            messagebox.showerror("Error", f"Ingresa valores validos.\nDetalle: {e}")
            return
        messagebox.showinfo("Exito", "Tarifas guardadas en nucleo/config_tarifas.py.")
        self.mostrar_administrador()

    def mostrar_matriz_floyd(self):
        try:
            datos = self._api("/floyd", timeout=8.0)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo obtener la matriz Floyd.\nDetalle: {e}")
            return

        municipios = datos["municipios"]
        distancias = datos["distancias"]
        ventana = tk.Toplevel(self.root)
        ventana.title("Matriz resultante de Floyd")
        ventana.geometry("980x560")
        ventana.configure(bg=COLOR_PANEL)

        self._label(
            ventana,
            "Matriz resultante de Floyd-Warshall",
            14,
            True,
            COLOR_TEXTO,
            anchor="w",
            padx=18,
            pady=(14, 4),
        )
        self._label(
            ventana,
            "Cada celda contiene la menor distancia en kilometros entre el municipio de la fila y el municipio de la columna.",
            9,
            color=COLOR_SUAVE,
            anchor="w",
            padx=18,
            pady=(0, 10),
        )

        contenedor = tk.Frame(ventana, bg=COLOR_PANEL)
        contenedor.pack(fill="both", expand=True, padx=18, pady=(0, 18))
        scroll_y = ttk.Scrollbar(contenedor, orient="vertical")
        scroll_x = ttk.Scrollbar(contenedor, orient="horizontal")
        texto = tk.Text(
            contenedor,
            wrap="none",
            bg="#f8fafc",
            fg=COLOR_TEXTO,
            font=("Consolas", 9),
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set,
        )
        scroll_y.config(command=texto.yview)
        scroll_x.config(command=texto.xview)
        scroll_y.pack(side="right", fill="y")
        scroll_x.pack(side="bottom", fill="x")
        texto.pack(side="left", fill="both", expand=True)

        encabezado = ["Origen/Destino"] + municipios
        filas = ["\t".join(encabezado)]
        for municipio, fila in zip(municipios, distancias):
            filas.append("\t".join([municipio] + [f"{valor:g}" for valor in fila]))
        texto.insert("1.0", "\n".join(filas))
        texto.config(state="disabled")

import tkinter as tk
from tkinter import ttk, messagebox

import requests
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from PIL import Image, ImageTk

import config_tarifas
import lector_excel
import visualizador_grafo


class AplicacionTransporte:
    def __init__(self, root):
        self.root = root
        self.root.title("Envios Rapidos GT - Planificador de Rutas")
        self.root.geometry("1250x720")
        self.root.minsize(1100, 650)
        self.root.config(bg="#f8fafc", padx=14, pady=14)

        self.municipios, self.matriz = lector_excel.cargar_datos()
        self.img_logo = None

        self._crear_layout()
        self._dibujar_grafo([])

    def _crear_layout(self):
        self.root.columnconfigure(0, weight=0, minsize=360)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

        panel_scroll = ttk.Frame(self.root)
        panel_scroll.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        panel_scroll.columnconfigure(0, weight=1)
        panel_scroll.rowconfigure(0, weight=1)

        canvas_izquierdo = tk.Canvas(panel_scroll, bg="#f8fafc", highlightthickness=0, width=360)
        scroll_izquierdo = ttk.Scrollbar(panel_scroll, orient="vertical", command=canvas_izquierdo.yview)
        canvas_izquierdo.configure(yscrollcommand=scroll_izquierdo.set)
        canvas_izquierdo.grid(row=0, column=0, sticky="nsew")
        scroll_izquierdo.grid(row=0, column=1, sticky="ns")

        panel_izquierdo = ttk.Frame(canvas_izquierdo, padding=12)
        ventana_panel = canvas_izquierdo.create_window((0, 0), window=panel_izquierdo, anchor="nw")
        panel_izquierdo.columnconfigure(0, weight=1)

        def actualizar_scroll(event):
            canvas_izquierdo.configure(scrollregion=canvas_izquierdo.bbox("all"))

        def ajustar_ancho(event):
            canvas_izquierdo.itemconfigure(ventana_panel, width=event.width)

        def activar_rueda(_event):
            canvas_izquierdo.bind_all("<MouseWheel>", mover_rueda)

        def desactivar_rueda(_event):
            canvas_izquierdo.unbind_all("<MouseWheel>")

        def mover_rueda(event):
            canvas_izquierdo.yview_scroll(int(-1 * (event.delta / 120)), "units")

        panel_izquierdo.bind("<Configure>", actualizar_scroll)
        canvas_izquierdo.bind("<Configure>", ajustar_ancho)
        canvas_izquierdo.bind("<Enter>", activar_rueda)
        canvas_izquierdo.bind("<Leave>", desactivar_rueda)

        panel_grafo = ttk.Frame(self.root, padding=8)
        panel_grafo.grid(row=0, column=1, sticky="nsew")
        panel_grafo.columnconfigure(0, weight=1)
        panel_grafo.rowconfigure(0, weight=1)

        self._crear_panel_cotizacion(panel_izquierdo)
        self._crear_panel_grafo(panel_grafo)

    def _crear_panel_cotizacion(self, contenedor):
        try:
            img_original = Image.open("logo.png")
            ancho_deseado = 180
            proporcion = ancho_deseado / float(img_original.size[0])
            alto_proporcional = int(float(img_original.size[1]) * proporcion)
            img_redimensionada = img_original.resize(
                (ancho_deseado, alto_proporcional),
                Image.Resampling.LANCZOS,
            )
            self.img_logo = ImageTk.PhotoImage(img_redimensionada)
            tk.Label(contenedor, image=self.img_logo).grid(row=0, column=0, pady=(0, 10))
        except Exception as e:
            print(f"Aviso: No se pudo cargar el logo ({e}). Se omitira.")

        ttk.Label(
            contenedor,
            text="Cotizador de Envios",
            font=("Arial", 18, "bold"),
        ).grid(row=1, column=0, sticky="w", pady=(0, 18))

        formulario = ttk.LabelFrame(contenedor, text="Datos del envio", padding=12)
        formulario.grid(row=2, column=0, sticky="ew")
        formulario.columnconfigure(0, weight=1)

        ttk.Label(formulario, text="Municipio de origen").grid(row=0, column=0, sticky="w")
        self.combo_origen = ttk.Combobox(formulario, values=self.municipios, state="readonly")
        self.combo_origen.grid(row=1, column=0, sticky="ew", pady=(4, 12))

        ttk.Label(formulario, text="Municipio de destino").grid(row=2, column=0, sticky="w")
        self.combo_destino = ttk.Combobox(formulario, values=self.municipios, state="readonly")
        self.combo_destino.grid(row=3, column=0, sticky="ew", pady=(4, 12))

        ttk.Label(formulario, text="Peso del paquete (libras)").grid(row=4, column=0, sticky="w")
        self.entry_peso = ttk.Entry(formulario)
        self.entry_peso.grid(row=5, column=0, sticky="ew", pady=(4, 14))

        tk.Button(
            formulario,
            text="Calcular ruta",
            bg="#0044cc",
            fg="white",
            activebackground="#003399",
            activeforeground="white",
            font=("Arial", 12, "bold"),
            relief="flat",
            command=self.calcular,
        ).grid(row=6, column=0, sticky="ew", ipady=8, pady=(0, 8))

        tk.Button(
            formulario,
            text="Reset",
            bg="#64748b",
            fg="white",
            activebackground="#475569",
            activeforeground="white",
            font=("Arial", 11, "bold"),
            relief="flat",
            command=self.resetear,
        ).grid(row=7, column=0, sticky="ew", ipady=6)

        self.frame_resultados = ttk.LabelFrame(contenedor, text="Calculo", padding=12)
        self.frame_resultados.grid(row=3, column=0, sticky="nsew", pady=(14, 0))
        self.frame_resultados.columnconfigure(0, weight=1)
        contenedor.rowconfigure(3, weight=1)

        self.lbl_ruta = ttk.Label(self.frame_resultados, text="Ruta: -", wraplength=310, justify="left")
        self.lbl_ruta.grid(row=0, column=0, sticky="nw", pady=(0, 12))

        self.lbl_km = tk.Label(
            self.frame_resultados,
            text="Distancia: -",
            font=("Arial", 12, "bold"),
            fg="blue",
            bg="#f8fafc",
            anchor="w",
        )
        self.lbl_km.grid(row=1, column=0, sticky="ew", pady=(0, 8))

        self.lbl_costo_total = ttk.Label(self.frame_resultados, text="Costo empresa: -", wraplength=310)
        self.lbl_costo_total.grid(row=2, column=0, sticky="w", pady=(0, 8))

        self.lbl_precio_final = tk.Label(
            self.frame_resultados,
            text="PRECIO A COBRAR: -",
            font=("Arial", 14, "bold"),
            fg="red",
            bg="#f8fafc",
            anchor="w",
        )
        self.lbl_precio_final.grid(row=3, column=0, sticky="ew")

    def _crear_panel_grafo(self, contenedor):
        self.figura = Figure(figsize=(8.5, 6.2), dpi=100)
        self.eje_grafo = self.figura.add_subplot(111)
        self.canvas_grafo = FigureCanvasTkAgg(self.figura, master=contenedor)
        self.canvas_grafo.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        self.toolbar_grafo = NavigationToolbar2Tk(self.canvas_grafo, contenedor, pack_toolbar=False)
        self.toolbar_grafo.update()
        self.toolbar_grafo.grid(row=1, column=0, sticky="ew", pady=(6, 0))

    def _dibujar_grafo(self, ruta):
        visualizador_grafo.dibujar_mapa(self.municipios, self.matriz, ruta, ax=self.eje_grafo)
        self.figura.tight_layout()
        self.canvas_grafo.draw_idle()

    def resetear(self):
        self.combo_origen.set("")
        self.combo_destino.set("")
        self.entry_peso.delete(0, tk.END)
        self.lbl_ruta.config(text="Ruta: -")
        self.lbl_km.config(text="Distancia: -")
        self.lbl_costo_total.config(text="Costo empresa: -")
        self.lbl_precio_final.config(text="PRECIO A COBRAR: -")
        self._dibujar_grafo([])

    def calcular(self):
        origen = self.combo_origen.get()
        destino = self.combo_destino.get()
        peso_txt = self.entry_peso.get()

        if not origen or not destino or not peso_txt:
            messagebox.showerror("Error", "Por favor llena todos los campos.")
            return

        try:
            peso = float(peso_txt)
            if peso <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "El peso debe ser un numero mayor que cero.")
            return

        try:
            respuesta = requests.post(
                "http://127.0.0.1:5000/calcular_ruta",
                json={"origen": origen, "destino": destino},
                timeout=8,
            )

            if respuesta.status_code != 200:
                error_msg = respuesta.json().get("error", "Error desconocido en el servidor.")
                messagebox.showerror("Aviso del Servidor", error_msg)
                return

            datos = respuesta.json()
            km = float(datos.get("distancia_km"))
            ruta = datos.get("ruta_optima")

            tarifas = config_tarifas.obtener()
            c_base = tarifas["COSTO_BASE"]
            c_km = tarifas["COSTO_POR_KM"]
            c_libra = tarifas["COSTO_POR_LIBRA"]
            utilidad = tarifas["MARGEN_UTILIDAD"]

            costo_total = c_base + (c_km * km) + (c_libra * peso)
            precio_final = costo_total + (costo_total * utilidad)

            ruta_texto = " -> ".join(ruta)
            self.lbl_ruta.config(text=f"Ruta: {ruta_texto}")
            self.lbl_km.config(text=f"Distancia: {km} kilometros")
            self.lbl_costo_total.config(
                text=f"Costo empresa: Q{costo_total:.2f} (Base: Q{c_base} | Km: Q{c_km} | Lb: Q{c_libra})"
            )
            self.lbl_precio_final.config(text=f"PRECIO A COBRAR: Q{precio_final:.2f}")

            self._dibujar_grafo(ruta)

        except requests.exceptions.ConnectionError:
            messagebox.showerror(
                "Error de conexion",
                "No se pudo conectar. Asegurate de que api_servidor.py este corriendo en otra terminal.",
            )
        except requests.exceptions.Timeout:
            messagebox.showerror("Error de conexion", "La API tardo demasiado en responder.")


if __name__ == "__main__":
    ventana = tk.Tk()
    app = AplicacionTransporte(ventana)
    ventana.mainloop()

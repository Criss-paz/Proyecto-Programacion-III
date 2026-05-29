import tkinter as tk
from tkinter import ttk, messagebox

import requests
from PIL import Image, ImageTk

import config_tarifas
import lector_excel
import visualizador_grafo


API_URL = "http://127.0.0.1:5000/calcular_ruta"


class AplicacionTransporte:
    def __init__(self, root):
        self.root = root
        self.root.title("Envios Rapidos GT - Planificador de Rutas")
        self.root.geometry("590x760")
        self.root.config(bg="#f8fafc", padx=18, pady=12)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(3, weight=1)

        self.municipios, self.matriz = lector_excel.cargar_datos()
        self.logo = None
        self.crear_interfaz()

    def crear_interfaz(self):
        self.mostrar_logo()
        ttk.Label(self.root, text="Cotizador", font=("Arial", 16, "bold")).grid(row=1, column=0, sticky="w")

        form = ttk.Frame(self.root)
        form.grid(row=2, column=0, sticky="ew", pady=8)
        self.origen = self.crear_campo(form, "Origen", ttk.Combobox, values=self.municipios, state="readonly")
        self.destino = self.crear_campo(form, "Destino", ttk.Combobox, values=self.municipios, state="readonly")
        self.peso = self.crear_campo(form, "Peso (lb)", ttk.Entry)

        tk.Button(form, text="Calcular ruta", bg="#0044cc", fg="white", command=self.calcular).pack(fill="x", ipady=5)
        tk.Button(form, text="Reset", bg="#64748b", fg="white", command=self.resetear).pack(fill="x", ipady=5, pady=6)

        resultado = ttk.LabelFrame(self.root, text="Calculo", padding=18)
        resultado.grid(row=3, column=0, sticky="nsew")

        self.labels = {
            "ruta": ttk.Label(resultado, text="Ruta: -", wraplength=520, justify="left"),
            "km": ttk.Label(resultado, text="Distancia: -", font=("Arial", 12, "bold"), foreground="blue"),
            "tarifas": ttk.Label(resultado, text="Tarifas: -"),
            "costo": ttk.Label(resultado, text="Costo empresa: -"),
            "precio": ttk.Label(resultado, text="PRECIO A COBRAR: -", font=("Arial", 15, "bold"), foreground="red"),
        }
        for label in self.labels.values():
            label.pack(anchor="w", pady=12)

    def mostrar_logo(self):
        try:
            imagen = Image.open("logo.png")
            alto = int(imagen.size[1] * 90 / imagen.size[0])
            self.logo = ImageTk.PhotoImage(imagen.resize((90, alto), Image.Resampling.LANCZOS))
            tk.Label(self.root, image=self.logo, bg="#f8fafc").grid(row=0, column=0)
        except Exception:
            pass

    def crear_campo(self, panel, texto, clase, **opciones):
        ttk.Label(panel, text=texto).pack(anchor="w")
        campo = clase(panel, **opciones)
        campo.pack(fill="x", pady=(2, 7))
        return campo

    def resetear(self):
        self.origen.set("")
        self.destino.set("")
        self.peso.delete(0, tk.END)
        textos = ["Ruta: -", "Distancia: -", "Tarifas: -", "Costo empresa: -", "PRECIO A COBRAR: -"]
        for label, texto in zip(self.labels.values(), textos):
            label.config(text=texto)

    def calcular(self):
        try:
            peso = float(self.peso.get())
            if not self.origen.get() or not self.destino.get() or peso <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Completa origen, destino y peso.")
            return

        try:
            respuesta = requests.post(
                API_URL,
                json={"origen": self.origen.get(), "destino": self.destino.get()},
                timeout=8,
            )
            datos = respuesta.json()
        except requests.exceptions.RequestException:
            messagebox.showerror("Error", "Ejecuta api_servidor.py antes de calcular.")
            return

        if "error" in datos:
            messagebox.showerror("Error", datos["error"])
            return

        self.mostrar_calculo(datos, peso)
        visualizador_grafo.dibujar_mapa(self.municipios, self.matriz, datos["ruta_optima"])

    def mostrar_calculo(self, datos, peso):
        km = float(datos["distancia_km"])
        ruta = datos["ruta_optima"]
        tarifas = config_tarifas.obtener()
        costo = tarifas["COSTO_BASE"] + tarifas["COSTO_POR_KM"] * km + tarifas["COSTO_POR_LIBRA"] * peso
        precio = costo * (1 + tarifas["MARGEN_UTILIDAD"])

        self.labels["ruta"].config(text=f"Ruta: {' -> '.join(ruta)}")
        self.labels["km"].config(text=f"Distancia: {km:.2f} kilometros")
        self.labels["tarifas"].config(
            text=f"Costo km: Q{tarifas['COSTO_POR_KM']:.2f} | "
            f"Costo libra: Q{tarifas['COSTO_POR_LIBRA']:.2f} | "
            f"Utilidad: {tarifas['MARGEN_UTILIDAD'] * 100:.0f}%"
        )
        self.labels["costo"].config(text=f"Costo empresa: Q{costo:.2f}")
        self.labels["precio"].config(text=f"PRECIO A COBRAR: Q{precio:.2f}")


if __name__ == "__main__":
    ventana = tk.Tk()
    AplicacionTransporte(ventana)
    ventana.mainloop()

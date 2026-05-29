import tkinter as tk
from tkinter import ttk, messagebox
import requests
from PIL import Image, ImageTk
import config_tarifas, lector_excel, visualizador_grafo

class AplicacionTransporte:
    def __init__(self, root):
        self.root = root
        self.root.title("Envíos Rápidos GT - Planificador")
        self.root.geometry("550x650")
        self.municipios, self.matriz = lector_excel.cargar_datos()
        self.construir_ui()

    def construir_ui(self):
        try:
            img = Image.open("logo.png").resize((200, 80), Image.Resampling.LANCZOS)
            self.logo = ImageTk.PhotoImage(img)
            tk.Label(self.root, image=self.logo).pack(pady=10)
        except: pass

        f = tk.Frame(self.root)
        f.pack(fill="x", padx=20)
        
        tk.Label(f, text="Origen:").pack(anchor="w")
        self.cb_origen = ttk.Combobox(f, values=self.municipios, state="readonly")
        self.cb_origen.pack(fill="x", pady=5)
        
        tk.Label(f, text="Destino:").pack(anchor="w")
        self.cb_destino = ttk.Combobox(f, values=self.municipios, state="readonly")
        self.cb_destino.pack(fill="x", pady=5)

        tk.Label(f, text="Peso (Libras):").pack(anchor="w")
        self.txt_peso = ttk.Entry(f)
        self.txt_peso.pack(fill="x", pady=5)

        tk.Button(f, text="Calcular Ruta y Precio", bg="#0044cc", fg="white", command=self.calcular).pack(pady=15, fill="x")

        self.lbl_resultados = tk.Label(self.root, text="-", justify="left", anchor="nw", font=("Arial", 11), wraplength=500)
        self.lbl_resultados.pack(fill="both", expand=True, padx=20)

    def calcular(self):
        try:
            peso = float(self.txt_peso.get())
            req = requests.post("http://127.0.0.1:5000/calcular_ruta", 
                                json={"origen": self.cb_origen.get(), "destino": self.cb_destino.get()})
            datos = req.json()
            
            if "error" in datos:
                messagebox.showerror("Error", datos["error"])
                return
                
            km = datos["distancia_km"]
            t = config_tarifas.obtener()
            costo = t["COSTO_BASE"] + (t["COSTO_POR_KM"] * km) + (t["COSTO_POR_LIBRA"] * peso)
            precio = costo * (1 + t["MARGEN_UTILIDAD"])

            texto = f"RUTA:\n{' -> '.join(datos['ruta_optima'])}\n\n"
            texto += f"Distancia: {km} km\nCosto Empresa: Q{costo:.2f}\n"
            texto += f"PRECIO FINAL: Q{precio:.2f}"
            self.lbl_resultados.config(text=texto, fg="black")
            
            visualizador_grafo.dibujar_mapa(self.municipios, self.matriz, datos["ruta_optima"])
            
        except Exception as e:
            messagebox.showerror("Error", "Revisa los campos numéricos y que el servidor esté activo.")

if __name__ == "__main__":
    vent = tk.Tk()
    AplicacionTransporte(vent)
    vent.mainloop()
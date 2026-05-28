import tkinter as tk
from tkinter import ttk, messagebox
import requests
import costos
import lector_excel

class AplicacionTransporte:
    def __init__(self, root):
        self.root = root
        self.root.title("Envíos Rápidos GT - Planificador de Rutas")
        self.root.geometry("500x600")
        self.root.config(padx=20, pady=20)

        # 1. Cargar lista de municipios para los menús desplegables
        municipios, _ = lector_excel.cargar_datos()
        
        # --- DISEÑO DE LA INTERFAZ ---
        # Título
        tk.Label(root, text="🚚 Cotizador de Envíos", font=("Arial", 18, "bold")).pack(pady=10)

        # Origen
        tk.Label(root, text="Municipio de Origen:").pack(anchor="w", pady=(10, 0))
        self.combo_origen = ttk.Combobox(root, values=municipios, state="readonly", width=40)
        self.combo_origen.pack()

        # Destino
        tk.Label(root, text="Municipio de Destino:").pack(anchor="w", pady=(10, 0))
        self.combo_destino = ttk.Combobox(root, values=municipios, state="readonly", width=40)
        self.combo_destino.pack()

        # Peso
        tk.Label(root, text="Peso del paquete (Libras):").pack(anchor="w", pady=(10, 0))
        self.entry_peso = ttk.Entry(root, width=43)
        self.entry_peso.pack()

        # Botón Calcular
        tk.Button(root, text="Calcular Ruta y Precio", bg="#0044cc", fg="white", font=("Arial", 12, "bold"), command=self.calcular).pack(pady=20)

        # --- ZONA DE RESULTADOS ---
        self.frame_resultados = tk.LabelFrame(root, text="Resumen del Envío", padx=10, pady=10)
        self.frame_resultados.pack(fill="both", expand=True)

        self.lbl_ruta = tk.Label(self.frame_resultados, text="-", wraplength=400, justify="left")
        self.lbl_ruta.pack(anchor="w")

        self.lbl_km = tk.Label(self.frame_resultados, text="-", font=("Arial", 12, "bold"), fg="blue")
        self.lbl_km.pack(anchor="w", pady=5)

        self.lbl_costo_total = tk.Label(self.frame_resultados, text="-")
        self.lbl_costo_total.pack(anchor="w")

        self.lbl_precio_final = tk.Label(self.frame_resultados, text="-", font=("Arial", 14, "bold"), fg="red")
        self.lbl_precio_final.pack(anchor="w", pady=5)

    def calcular(self):
        origen = self.combo_origen.get()
        destino = self.combo_destino.get()
        peso_txt = self.entry_peso.get()

        # Validaciones de seguridad
        if not origen or not destino or not peso_txt:
            messagebox.showerror("Error", "Por favor llena todos los campos.")
            return
        
        try:
            peso = float(peso_txt)
        except ValueError:
            messagebox.showerror("Error", "El peso debe ser un número.")
            return

        # 3. Petición a la API (El Cerebro)
        try:
            url_api = "http://127.0.0.1:5000/calcular_ruta"
            datos_enviar = {"origen": origen, "destino": destino}
            
            # Mandamos el mensaje por internet local
            respuesta = requests.post(url_api, json=datos_enviar)
            datos = respuesta.json()

            # 4. Extraemos la respuesta de la API
            km = datos.get("distancia_km")
            ruta = datos.get("ruta_optima")

            # 5. Calculamos el dinero llamando a costos.py
            c_base, c_km, c_libra, costo_total, precio_final = costos.calcular_factura(km, peso)

            # 6. Actualizamos la pantalla (con los colores que pide el PDF)
            ruta_texto = " -> ".join(ruta)
            self.lbl_ruta.config(text=f"Ruta: {ruta_texto}")
            self.lbl_km.config(text=f"Distancia: {km} kilómetros")
            self.lbl_costo_total.config(text=f"Costo Total Empresa: Q{costo_total:.2f}\n(Base: Q{c_base} | Por Km: Q{c_km} | Por Lb: Q{c_libra})")
            self.lbl_precio_final.config(text=f"PRECIO A COBRAR (con utilidad): Q{precio_final:.2f}")

        except requests.exceptions.ConnectionError:
            messagebox.showerror("Error de Conexión", "No se pudo conectar con la API. Asegúrate de que api_servidor.py esté corriendo.")


# Arrancar la ventana
if __name__ == "__main__":
    ventana = tk.Tk()
    app = AplicacionTransporte(ventana)
    ventana.mainloop()
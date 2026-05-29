import tkinter as tk
from tkinter import ttk, messagebox
import requests
import config_tarifas
from PIL import Image, ImageTk
import lector_excel
import visualizador_grafo  # <--- SE AGREGÓ ESTA LÍNEA

class AplicacionTransporte:
    def __init__(self, root):
        self.root = root
        self.root.title("Envíos Rápidos GT - Planificador de Rutas")
        self.root.geometry("550x600")
        self.root.config(padx=20, pady=20)

        # 1. Cargamos municipios Y LA MATRIZ desde el inicio
        self.municipios, self.matriz = lector_excel.cargar_datos()
        
# --- DISEÑO DE LA INTERFAZ ---
        # Cargar y redimensionar el logo PROFESIONALMENTE con Pillow
        try:
            # 1. Abrir la imagen original (asegúrate de que el nombre coincida)
            img_original = Image.open("logo.png")

            # 2. Definir el ancho deseado (ej: 200 píxeles para que se vea decente pero no gigante)
            # Prueba con 200 o 250 hasta que te guste cómo se ve.
            ANCHO_DESEADO = 200

            # 3. Calcular el alto proporcionalmente para no deformar el logo
            proporcion = ANCHO_DESEADO / float(img_original.size[0])
            alto_proporcional = int(float(img_original.size[1]) * float(proporcion))

            # 4. Redimensionar usando la mejor calidad (LANCZOS)
            img_redimensionada = img_original.resize((ANCHO_DESEADO, alto_proporcional), Image.Resampling.LANCZOS)

            # 5. Convertir al formato que Tkinter entiende
            self.img_logo = ImageTk.PhotoImage(img_redimensionada)

            # 6. Mostrar el logo en pantalla con márgenes limpios
            tk.Label(root, image=self.img_logo).pack(pady=(10, 5))

        except Exception as e:
            # Si hay un error con el logo, el programa sigue corriendo sin él
            print(f"Aviso: No se pudo cargar el logo ({e}). Se omitirá.")

        # Título del cotizador (mantenemos esto igual, solo ajustamos márgenes)
        tk.Label(root, text="🚚 Cotizador de Envíos", font=("Arial", 18, "bold")).pack(pady=(0, 10))

        tk.Label(root, text="Municipio de Origen:").pack(anchor="w", pady=(10, 0))
        self.combo_origen = ttk.Combobox(root, values=self.municipios, state="readonly", width=40)
        self.combo_origen.pack()

        tk.Label(root, text="Municipio de Destino:").pack(anchor="w", pady=(10, 0))
        self.combo_destino = ttk.Combobox(root, values=self.municipios, state="readonly", width=40)
        self.combo_destino.pack()

        tk.Label(root, text="Peso del paquete (Libras):").pack(anchor="w", pady=(10, 0))
        self.entry_peso = ttk.Entry(root, width=43)
        self.entry_peso.pack()

        tk.Button(root, text="Calcular Ruta y Ver Mapa", bg="#0044cc", fg="white", 
                  font=("Arial", 12, "bold"), command=self.calcular).pack(pady=20)

        # --- ZONA DE RESULTADOS ---
        self.frame_resultados = tk.LabelFrame(root, text="Resumen del Envío", padx=10, pady=10)
        self.frame_resultados.pack(fill="both", expand=True)

        self.lbl_ruta = tk.Label(self.frame_resultados, text="-", wraplength=450, justify="left")
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

        if not origen or not destino or not peso_txt:
            messagebox.showerror("Error", "Por favor llena todos los campos.")
            return
        
        try:
            peso = float(peso_txt)
        except ValueError:
            messagebox.showerror("Error", "El peso debe ser un número.")
            return

        try:
            url_api = "http://127.0.0.1:5000/calcular_ruta"
            datos_enviar = {"origen": origen, "destino": destino}
            
            respuesta = requests.post(url_api, json=datos_enviar)
            
            if respuesta.status_code != 200:
                error_msg = respuesta.json().get("error", "Error desconocido en el servidor.")
                messagebox.showerror("Aviso del Servidor", error_msg)
                return
                
            datos = respuesta.json()
            km = float(datos.get("distancia_km"))
            ruta = datos.get("ruta_optima")

# Leemos directamente del archivo de configuración sin poner valores por defecto aquí
            tarifas = config_tarifas.obtener()
            c_base = tarifas["COSTO_BASE"]
            c_km = tarifas["COSTO_POR_KM"]
            c_libra = tarifas["COSTO_POR_LIBRA"]
            utilidad = tarifas["MARGEN_UTILIDAD"]

            costo_total = c_base + (c_km * km) + (c_libra * peso)
            precio_final = costo_total + (costo_total * utilidad)

            ruta_texto = " -> ".join(ruta)
            self.lbl_ruta.config(text=f"Ruta: {ruta_texto}")
            self.lbl_km.config(text=f"Distancia: {km} kilómetros")
            self.lbl_costo_total.config(text=f"Costo Empresa: Q{costo_total:.2f} (Base: Q{c_base} | Km: Q{c_km} | Lb: Q{c_libra})")
            self.lbl_precio_final.config(text=f"PRECIO A COBRAR: Q{precio_final:.2f}")

            # 7. ¡LA MAGIA DEL MAPA! Llamamos al visualizador
            visualizador_grafo.dibujar_mapa(self.municipios, self.matriz, ruta)

        except requests.exceptions.ConnectionError:
            messagebox.showerror("Error de Conexión", "No se pudo conectar. Asegúrate de que 'api_servidor.py' esté corriendo en otra terminal.")

if __name__ == "__main__":
    ventana = tk.Tk()
    app = AplicacionTransporte(ventana)
    ventana.mainloop()
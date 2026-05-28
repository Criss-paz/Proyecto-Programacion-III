# cliente_ui.py
import tkinter as tk
from tkinter import ttk, messagebox
import requests
import costos
import lector_excel

class VistaCajero(tk.Frame):
    """Pantalla para que el cajero cotice los envios."""
    def __init__(self, parent, municipios):
        super().__init__(parent, bg="#f4f6f9")
        
        # Encabezado corporativo (Logo en texto)
        self.header = tk.Frame(self, bg="#1a252f", pady=12)
        self.header.pack(fill="x", pady=(0, 10))
        tk.Label(self.header, text="🚚 [ GT-EXPRESS S.A. ]", font=("Arial", 16, "bold"), fg="#2ecc71", bg="#1a252f").pack()
        tk.Label(self.header, text="Modulo de Caja y Cotizaciones", font=("Arial", 10, "italic"), fg="#bdc3c7", bg="#1a252f").pack()

        # Formulario de datos
        self.formulario = tk.LabelFrame(self, text=" Datos del Paquete ", font=("Arial", 10, "bold"), padx=15, pady=10)
        self.formulario.pack(fill="x", pady=5, padx=15)

        tk.Label(self.formulario, text="Municipio Origen:").pack(anchor="w")
        self.combo_origen = ttk.Combobox(self.formulario, values=municipios, state="readonly")
        self.combo_origen.pack(fill="x", pady=5)

        tk.Label(self.formulario, text="Municipio Destino:").pack(anchor="w")
        self.combo_destino = ttk.Combobox(self.formulario, values=municipios, state="readonly")
        self.combo_destino.pack(fill="x", pady=5)

        tk.Label(self.formulario, text="Peso del Paquete (Libras):").pack(anchor="w")
        self.entry_peso = ttk.Entry(self.formulario)
        self.entry_peso.pack(fill="x", pady=5)

        # Botones de Accion
        self.botones = tk.Frame(self)
        self.botones.pack(fill="x", pady=10, padx=15)
        tk.Button(self.botones, text="CALCULAR ENVIO", bg="#27ae60", fg="white", font=("Arial", 10, "bold"), command=self.calcular, height=2, width=20).pack(side="left", expand=True, padx=5)
        tk.Button(self.botones, text="LIMPIAR PANTALLA", bg="#7f8c8d", fg="white", font=("Arial", 10, "bold"), command=self.limpiar, height=2, width=20).pack(side="right", expand=True, padx=5)

        # Panel de Resultados Exigidos
        self.resultados = tk.LabelFrame(self, text=" Resumen de Tarifas ", font=("Arial", 10, "bold"), padx=15, pady=10)
        self.resultados.pack(fill="both", expand=True, pady=5, padx=15)

        # Distancias en AZUL
        self.lbl_dijkstra = tk.Label(self.resultados, text="Distancia (Dijkstra): - KM", font=("Arial", 11, "bold"), fg="blue")
        self.lbl_dijkstra.pack(anchor="w", pady=2)
        self.lbl_floyd = tk.Label(self.resultados, text="Distancia (Floyd): - KM", font=("Arial", 11, "bold"), fg="blue")
        self.lbl_floyd.pack(anchor="w", pady=2)

        self.lbl_ruta = tk.Label(self.resultados, text="Ruta sugerida: -", wraplength=440, justify="left", font=("Arial", 10))
        self.lbl_ruta.pack(anchor="w", pady=6)

        self.lbl_costo_total = tk.Label(self.resultados, text="Costo Operativo Total: Q0.00", font=("Arial", 10, "bold"))
        self.lbl_costo_total.pack(anchor="w", pady=2)
        
        self.lbl_desglose = tk.Label(self.resultados, text="(Base: Q0.00 | Por Km: Q0.00 | Por Lb: Q0.00)", font=("Arial", 9, "italic"), fg="gray")
        self.lbl_desglose.pack(anchor="w", pady=1)

        # Precio Final en ROJO
        self.lbl_precio_final = tk.Label(self.resultados, text="PRECIO TOTAL A PAGAR: Q0.00", font=("Arial", 14, "bold"), fg="red")
        self.lbl_precio_final.pack(anchor="w", pady=10)

    def limpiar(self):
        self.combo_origen.set('')
        self.combo_destino.set('')
        self.entry_peso.delete(0, tk.END)
        self.lbl_dijkstra.config(text="Distancia (Dijkstra): - KM")
        self.lbl_floyd.config(text="Distancia (Floyd): - KM")
        self.lbl_ruta.config(text="Ruta sugerida: -")
        self.lbl_costo_total.config(text="Costo Operativo Total: Q0.00")
        self.lbl_desglose.config(text="(Base: Q0.00 | Por Km: Q0.00 | Por Lb: Q0.00)")
        self.lbl_precio_final.config(text="PRECIO TOTAL A PAGAR: Q0.00")

    def calcular(self):
        origen = self.combo_origen.get()
        destino = self.combo_destino.get()
        peso_txt = self.entry_peso.get()

        if not origen or not destino or not peso_txt:
            messagebox.showerror("Campos Vacios", "Por favor llena todos los campos.")
            return
        try:
            peso = float(peso_txt)
            if peso <= 0: raise ValueError
        except ValueError:
            messagebox.showerror("Error de Peso", "El peso debe ser un numero valido mayor a 0.")
            return

        try:
            url_api = "http://127.0.0"
            respuesta = requests.post(url_api, json={"origen": origen, "destino": destino})
            
            if respuesta.status_code == 200:
                datos = respuesta.json()
                km = datos.get("distancia_km", 0.0)
                ruta_nodos = datos.get("ruta_optima", [])

                c_base, c_km, c_libra, costo_total, precio_final = costos.calcular_factura(km, peso)

                self.lbl_ruta.config(text=f"Ruta sugerida: {' ➔ '.join(ruta_nodos)}")
                self.lbl_dijkstra.config(text=f"Distancia (Dijkstra): {km} KM")
                self.lbl_floyd.config(text=f"Distancia (Floyd): {km} KM")
                self.lbl_costo_total.config(text=f"Costo Operativo Total: Q{costo_total:.2f}")
                self.lbl_desglose.config(text=f"(Base: Q{c_base:.2f} | Por Km: Q{c_km:.2f} | Por Lb: Q{c_libra:.2f})")
                self.lbl_precio_final.config(text=f"PRECIO TOTAL A PAGAR: Q{precio_final:.2f}")
            else:
                messagebox.showerror("Error", "No se encontro una ruta transitable.")
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Falla de API", "No hay conexion con el servidor.\nEnciende primero el archivo api_servidor.py.")


class VistaAdministrador(tk.Frame):
    """Pantalla gerencial para auditar los costos de la empresa."""
    def __init__(self, parent):
        super().__init__(parent, bg="#f4f6f9")
        
        self.header = tk.Frame(self, bg="#2c3e50", pady=12)
        self.header.pack(fill="x", pady=(0, 10))
        tk.Label(self.header, text=" PANEL DE CONFIGURACION GERENCIAL", font=("Arial", 12, "bold"), fg="white", bg="#2c3e50").pack()

        self.info = tk.LabelFrame(self, text=" Tarifas Vigentes de la Empresa ", font=("Arial", 10, "bold"), padx=15, pady=15)
        self.info.pack(fill="x", pady=20, padx=15)

        tk.Label(self.info, text=f"• Costo Operativo Base Fijo: Q{costos.costo_base:.2f}", font=("Arial", 10)).pack(anchor="w", pady=6)
        tk.Label(self.info, text=f"• Tarifa por Kilometro Recorrido: Q{costos.costo_km:.2f}", font=("Arial", 10)).pack(anchor="w", pady=6)
        tk.Label(self.info, text=f"• Tarifa por Libra de Peso: Q{costos.costo_libra:.2f}", font=("Arial", 10)).pack(anchor="w", pady=6)
        tk.Label(self.info, text=f"• Porcentaje de Utilidad Comercial: {costos.utilidad * 100:.0f}%", font=("Arial", 10), fg="green").pack(anchor="w", pady=6)

        self.auditoria = tk.LabelFrame(self, text=" Justificacion Tecnica del Grupo ", font=("Arial", 9, "bold"), padx=10, pady=10)
        self.auditoria.pack(fill="both", expand=True, padx=15, pady=10)
        
        explicacion = (
            "Estas tarifas se estructuraron analizando factores de logistica real en Guatemala:\n\n"
            "- El costo por kilometro financia el combustible y el desgaste de los camiones.\n"
            "- La utilidad del 30% cubre el margen de ganancia de la empresa sin violar los rangos del PDF."
        )
        tk.Label(self.auditoria, text=explicacion, wraplength=400, justify="left", font=("Arial", 9, "italic"), fg="#555").pack()

import tkinter as tk
from tkinter import ttk, messagebox

import algoritmos
import costos
import lector_excel

try:
    import requests
except ModuleNotFoundError:
    requests = None


COLOR_FONDO = "#eef2f7"
COLOR_TARJETA = "#ffffff"
COLOR_TEXTO = "#172033"
COLOR_SECUNDARIO = "#667085"
COLOR_PRIMARIO = "#2563eb"
COLOR_PRIMARIO_OSCURO = "#1d4ed8"
COLOR_EXITO = "#047857"
COLOR_ALERTA = "#b42318"


class VistaCajero(ttk.Frame):
    def __init__(self, parent, municipios):
        super().__init__(parent, padding=20)
        tk.Label(self, text="Cotizador de Envios", font=("Segoe UI", 18, "bold")).pack(pady=10)
        tk.Label(self, text=f"Municipios disponibles: {len(municipios)}").pack(pady=10)


class VistaAdministrador(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=20)
        tk.Label(self, text="Panel de Administrador", font=("Segoe UI", 18, "bold")).pack(pady=10)


class AplicacionTransporte:
    def __init__(self, root):
        self.root = root
        self.root.title("Envios Rapidos GT - Aplicacion de Escritorio")
        self.root.geometry("840x640")
        self.root.minsize(760, 560)
        self.root.configure(bg=COLOR_FONDO)

        self.municipios, self.matriz = lector_excel.cargar_datos()
        self.vista_actual = None

        self._configurar_estilos()
        self._crear_estructura()
        self.mostrar_cotizador()

    def _configurar_estilos(self):
        self.estilo = ttk.Style()
        self.estilo.theme_use("clam")
        self.estilo.configure("TCombobox", padding=8, font=("Segoe UI", 10))
        self.estilo.configure("TEntry", padding=8, font=("Segoe UI", 10))

    def _crear_estructura(self):
        self.header = tk.Frame(self.root, bg="#111827", height=88)
        self.header.pack(fill="x")
        self.header.pack_propagate(False)

        titulo = tk.Label(
            self.header,
            text="Envios Rapidos GT",
            bg="#111827",
            fg="#ffffff",
            font=("Segoe UI", 20, "bold"),
        )
        titulo.pack(side="left", padx=28)

        subtitulo = tk.Label(
            self.header,
            text="Cotizador y panel administrativo",
            bg="#111827",
            fg="#cbd5e1",
            font=("Segoe UI", 10),
        )
        subtitulo.pack(side="left", padx=(0, 18))

        self.btn_admin = tk.Button(
            self.header,
            text="Administrador",
            command=self.mostrar_administrador,
            bg="#374151",
            fg="#ffffff",
            activebackground="#4b5563",
            activeforeground="#ffffff",
            relief="flat",
            bd=0,
            padx=18,
            pady=10,
            cursor="hand2",
            font=("Segoe UI", 10, "bold"),
        )
        self.btn_admin.pack(side="right", padx=(8, 28))

        self.btn_cotizador = tk.Button(
            self.header,
            text="Cotizador",
            command=self.mostrar_cotizador,
            bg=COLOR_PRIMARIO,
            fg="#ffffff",
            activebackground=COLOR_PRIMARIO_OSCURO,
            activeforeground="#ffffff",
            relief="flat",
            bd=0,
            padx=18,
            pady=10,
            cursor="hand2",
            font=("Segoe UI", 10, "bold"),
        )
        self.btn_cotizador.pack(side="right", padx=8)

        self.contenido = tk.Frame(self.root, bg=COLOR_FONDO)
        self.contenido.pack(fill="both", expand=True, padx=24, pady=22)

    def _limpiar_contenido(self):
        for widget in self.contenido.winfo_children():
            widget.destroy()

    def _tarjeta(self, parent):
        frame = tk.Frame(parent, bg=COLOR_TARJETA, highlightbackground="#d0d5dd", highlightthickness=1)
        return frame

    def _titulo_seccion(self, parent, titulo, descripcion):
        tk.Label(
            parent,
            text=titulo,
            bg=COLOR_TARJETA,
            fg=COLOR_TEXTO,
            font=("Segoe UI", 18, "bold"),
        ).pack(anchor="w", padx=22, pady=(20, 2))
        tk.Label(
            parent,
            text=descripcion,
            bg=COLOR_TARJETA,
            fg=COLOR_SECUNDARIO,
            font=("Segoe UI", 10),
        ).pack(anchor="w", padx=22, pady=(0, 16))

    def _etiqueta(self, parent, texto):
        tk.Label(
            parent,
            text=texto,
            bg=COLOR_TARJETA,
            fg=COLOR_TEXTO,
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w", padx=22, pady=(10, 4))

    def _boton_principal(self, parent, texto, comando):
        return tk.Button(
            parent,
            text=texto,
            command=comando,
            bg=COLOR_PRIMARIO,
            fg="#ffffff",
            activebackground=COLOR_PRIMARIO_OSCURO,
            activeforeground="#ffffff",
            relief="flat",
            bd=0,
            padx=18,
            pady=12,
            cursor="hand2",
            font=("Segoe UI", 11, "bold"),
        )

    def mostrar_cotizador(self):
        self.vista_actual = "cotizador"
        self._limpiar_contenido()
        self.btn_cotizador.configure(bg=COLOR_PRIMARIO)
        self.btn_admin.configure(bg="#374151")

        panel = tk.Frame(self.contenido, bg=COLOR_FONDO)
        panel.pack(fill="both", expand=True)
        panel.columnconfigure(0, weight=1)
        panel.columnconfigure(1, weight=1)
        panel.rowconfigure(0, weight=1)

        formulario = self._tarjeta(panel)
        formulario.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        resultado = self._tarjeta(panel)
        resultado.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        self._titulo_seccion(formulario, "Cotizador", "Ingrese los datos del envio para calcular ruta y precio.")

        self._etiqueta(formulario, "Municipio de origen")
        self.combo_origen = ttk.Combobox(formulario, values=self.municipios, state="readonly", width=34)
        self.combo_origen.pack(anchor="w", fill="x", padx=22)

        self._etiqueta(formulario, "Municipio de destino")
        self.combo_destino = ttk.Combobox(formulario, values=self.municipios, state="readonly", width=34)
        self.combo_destino.pack(anchor="w", fill="x", padx=22)

        self._etiqueta(formulario, "Peso del paquete en libras")
        self.entry_peso = ttk.Entry(formulario)
        self.entry_peso.pack(anchor="w", fill="x", padx=22)

        self._boton_principal(formulario, "Calcular ruta y precio", self.calcular).pack(
            anchor="w",
            padx=22,
            pady=22,
        )

        self._titulo_seccion(resultado, "Resumen", "Aqui aparecera el resultado del calculo.")

        self.lbl_ruta = tk.Label(
            resultado,
            text="Ruta: -",
            bg=COLOR_TARJETA,
            fg=COLOR_TEXTO,
            justify="left",
            wraplength=320,
            font=("Segoe UI", 10),
        )
        self.lbl_ruta.pack(anchor="w", padx=22, pady=(8, 12))

        self.lbl_km = tk.Label(
            resultado,
            text="Distancia: -",
            bg=COLOR_TARJETA,
            fg=COLOR_PRIMARIO,
            font=("Segoe UI", 15, "bold"),
        )
        self.lbl_km.pack(anchor="w", padx=22, pady=8)

        self.lbl_costo_total = tk.Label(
            resultado,
            text="Costo total empresa: -",
            bg=COLOR_TARJETA,
            fg=COLOR_SECUNDARIO,
            justify="left",
            font=("Segoe UI", 10),
        )
        self.lbl_costo_total.pack(anchor="w", padx=22, pady=8)

        self.lbl_precio_final = tk.Label(
            resultado,
            text="Precio a cobrar: -",
            bg=COLOR_TARJETA,
            fg=COLOR_ALERTA,
            justify="left",
            wraplength=320,
            font=("Segoe UI", 16, "bold"),
        )
        self.lbl_precio_final.pack(anchor="w", padx=22, pady=(16, 8))

    def mostrar_administrador(self):
        self.vista_actual = "administrador"
        self._limpiar_contenido()
        self.btn_admin.configure(bg=COLOR_PRIMARIO)
        self.btn_cotizador.configure(bg="#374151")

        panel = self._tarjeta(self.contenido)
        panel.pack(fill="both", expand=True, padx=8, pady=8)
        self._titulo_seccion(panel, "Administrador", "Herramientas para revisar la informacion del sistema.")

        datos = tk.Frame(panel, bg=COLOR_TARJETA)
        datos.pack(fill="x", padx=22, pady=8)
        datos.columnconfigure(0, weight=1)
        datos.columnconfigure(1, weight=1)
        datos.columnconfigure(2, weight=1)

        self.lbl_municipios = self._crear_indicador(datos, "Municipios", str(len(self.municipios)), 0)
        matriz_texto = f"{self.matriz.shape[0]} x {self.matriz.shape[1]}" if self.matriz.size else "Sin datos"
        self.lbl_matriz = self._crear_indicador(datos, "Matriz", matriz_texto, 1)
        self.lbl_archivo = self._crear_indicador(datos, "Archivo Excel", "Cargado" if len(self.municipios) else "Pendiente", 2)

        acciones = tk.Frame(panel, bg=COLOR_TARJETA)
        acciones.pack(fill="x", padx=22, pady=18)

        self._boton_principal(acciones, "Verificar Excel", self.verificar_excel).pack(side="left", padx=(0, 10))
        self._boton_principal(acciones, "Recargar datos", self.recargar_datos).pack(side="left", padx=10)

        tk.Button(
            acciones,
            text="Volver al cotizador",
            command=self.mostrar_cotizador,
            bg="#f3f4f6",
            fg=COLOR_TEXTO,
            activebackground="#e5e7eb",
            relief="flat",
            bd=0,
            padx=18,
            pady=12,
            cursor="hand2",
            font=("Segoe UI", 11, "bold"),
        ).pack(side="left", padx=10)

        self.lbl_estado_admin = tk.Label(
            panel,
            text="Listo para revisar el archivo distancias.xlsx.",
            bg=COLOR_TARJETA,
            fg=COLOR_SECUNDARIO,
            justify="left",
            wraplength=720,
            font=("Segoe UI", 10),
        )
        self.lbl_estado_admin.pack(anchor="w", padx=22, pady=(8, 14))

        self.lista_admin = tk.Listbox(
            panel,
            height=9,
            bg="#f8fafc",
            fg=COLOR_TEXTO,
            highlightthickness=1,
            highlightbackground="#d0d5dd",
            bd=0,
            font=("Segoe UI", 10),
        )
        self.lista_admin.pack(fill="both", expand=True, padx=22, pady=(0, 22))
        self._llenar_lista_municipios()

    def _crear_indicador(self, parent, titulo, valor, columna):
        caja = tk.Frame(parent, bg="#f8fafc", highlightbackground="#d0d5dd", highlightthickness=1)
        caja.grid(row=0, column=columna, sticky="ew", padx=6, ipady=12)

        tk.Label(caja, text=titulo, bg="#f8fafc", fg=COLOR_SECUNDARIO, font=("Segoe UI", 9, "bold")).pack()
        etiqueta = tk.Label(caja, text=valor, bg="#f8fafc", fg=COLOR_TEXTO, font=("Segoe UI", 15, "bold"))
        etiqueta.pack()
        return etiqueta

    def _llenar_lista_municipios(self):
        self.lista_admin.delete(0, tk.END)
        if not self.municipios:
            self.lista_admin.insert(tk.END, "No hay municipios cargados.")
            return

        for indice, municipio in enumerate(self.municipios[:20], start=1):
            self.lista_admin.insert(tk.END, f"{indice}. {municipio}")

    def recargar_datos(self):
        self.municipios, self.matriz = lector_excel.cargar_datos()
        self.lbl_municipios.config(text=str(len(self.municipios)))
        matriz_texto = f"{self.matriz.shape[0]} x {self.matriz.shape[1]}" if self.matriz.size else "Sin datos"
        self.lbl_matriz.config(text=matriz_texto)
        self.lbl_archivo.config(text="Cargado" if len(self.municipios) else "Pendiente")
        self._llenar_lista_municipios()
        self.lbl_estado_admin.config(text="Datos recargados desde distancias.xlsx.")

    def verificar_excel(self):
        if len(self.municipios) == 0:
            self.lbl_estado_admin.config(
                fg=COLOR_ALERTA,
                text="No se pudieron cargar municipios desde distancias.xlsx.",
            )
            return

        self.lbl_estado_admin.config(
            fg=COLOR_EXITO,
            text=(
                "El archivo Excel se leyo correctamente.\n"
                f"Municipios cargados: {len(self.municipios)}\n"
                f"Dimension de matriz: {self.matriz.shape}"
            ),
        )

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
            messagebox.showerror("Error", "El peso debe ser un numero.")
            return

        if peso <= 0:
            messagebox.showerror("Error", "El peso debe ser mayor que cero.")
            return

        try:
            km, ruta = self._calcular_ruta(origen, destino)
        except Exception as error:
            messagebox.showerror("Error", f"No se pudo calcular la ruta: {error}")
            return

        if not ruta:
            messagebox.showerror("Sin ruta", "No existe una ruta disponible entre esos municipios.")
            return

        c_base, c_km, c_libra, costo_total, precio_final = costos.calcular_factura(km, peso)

        ruta_texto = " -> ".join(ruta)
        self.lbl_ruta.config(text=f"Ruta: {ruta_texto}")
        self.lbl_km.config(text=f"Distancia: {km} kilometros")
        self.lbl_costo_total.config(
            text=(
                f"Costo total empresa: Q{costo_total:.2f}\n"
                f"Base: Q{c_base:.2f} | Por km: Q{c_km:.2f} | Por lb: Q{c_libra:.2f}"
            )
        )
        self.lbl_precio_final.config(text=f"Precio a cobrar: Q{precio_final:.2f}")

    def _calcular_ruta(self, origen, destino):
        datos_api = self._consultar_api(origen, destino)
        if datos_api is not None:
            return datos_api["distancia_km"], datos_api["ruta_optima"]

        return algoritmos.calcular_ruta_floyd(self.matriz, self.municipios, origen, destino)

    def _consultar_api(self, origen, destino):
        if requests is None:
            return None

        try:
            respuesta = requests.post(
                "http://127.0.0.1:5000/calcular_ruta",
                json={"origen": origen, "destino": destino},
                timeout=2,
            )
            respuesta.raise_for_status()
            return respuesta.json()
        except requests.exceptions.RequestException:
            return None


if __name__ == "__main__":
    ventana = tk.Tk()
    AplicacionTransporte(ventana)
    ventana.mainloop()

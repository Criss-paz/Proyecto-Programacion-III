"""Pantalla Cotizador: formulario, cálculo de ruta y mapa."""

import tkinter as tk
from tkinter import messagebox, ttk
from nucleo import config_tarifas
from cliente import visualizador_grafo
from cliente.ui_helpers import COLOR_PANEL, COLOR_TEXTO, COLOR_BORDE, COLOR_ERROR, ScrollableFrame


class VistaCotizador:
    def mostrar_cotizador(self):
        self.contenido.columnconfigure(0, weight=0, minsize=350)
        self.contenido.columnconfigure(1, weight=1)
        self.contenido.rowconfigure(0, weight=1)

        form = self._panel(self.contenido, row=0, column=0, sticky="nsew", padx=(0, 14))
        scroll = ScrollableFrame(form)
        scroll.pack(fill="both", expand=True)

        mapa = self._panel(self.contenido, row=0, column=1, sticky="nsew")
        mapa.rowconfigure(1, weight=1)
        mapa.columnconfigure(0, weight=1)

        self._crear_formulario(scroll.scrollable_frame)
        self._crear_mapa(mapa)
        self.root.after(120, lambda: self._mostrar_mapa([]))

    def _crear_formulario(self, parent):
        self._titulo(parent, "Cotizador", "Selecciona origen, destino y peso.")
        self.combo_origen = ttk.Combobox(parent, values=self.municipios, state="readonly")
        self.combo_destino = ttk.Combobox(parent, values=self.municipios, state="readonly")
        self.entry_peso = ttk.Entry(parent)
        for combo in (self.combo_origen, self.combo_destino):
            combo.bind("<<ComboboxSelected>>", self.actualizar_grafo_por_seleccion)

        self._campo(parent, "Origen", self.combo_origen)
        self._campo(parent, "Destino", self.combo_destino)
        self._campo(parent, "Peso en libras", self.entry_peso)

        acciones = tk.Frame(parent, bg=COLOR_PANEL)
        acciones.pack(fill="x", padx=20, pady=18)
        self._boton(acciones, "Calcular", self.calcular, primario=True).pack(side="left")
        self._boton(acciones, "Limpiar", self.reiniciar_cotizacion).pack(side="left", padx=8)
        tk.Frame(parent, bg=COLOR_BORDE, height=1).pack(fill="x", padx=20, pady=(4, 14))

        self.lbl_ruta = self._resultado(parent, "Ruta", "-")
        self.lbl_km = self._resultado(parent, "Distancia (Kilómetros)", "-", color_resaltado="#2563eb")
        self.lbl_costo_total = self._resultado(parent, "Desglose de Costos", "-")
        self.lbl_precio_final = self._resultado(parent, "Precio Final (Cobro al cliente)", "-", color_resaltado="#ef4444", grande=True)

    def _crear_mapa(self, parent):
        enc = tk.Frame(parent, bg=COLOR_PANEL)
        enc.grid(row=0, column=0, sticky="ew", padx=18, pady=(14, 8))
        tk.Label(enc, text="Rutas Municipales", bg=COLOR_PANEL, fg=COLOR_TEXTO, font=("Segoe UI", 16, "bold")).pack(side="left")

        controles = tk.Frame(enc, bg=COLOR_PANEL)
        controles.pack(side="right")

        def cmd(zoom, dx=0, dy=0, centrar=False):
            if centrar:
                self.zoom_grafo, self.desplazamiento_grafo = 1.0, (0.0, 0.0)
            else:
                self.zoom_grafo = max(0.5, min(self.zoom_grafo * zoom, 4.0))
                paso = 0.25 / max(self.zoom_grafo, 1.0)
                ax, ay = self.desplazamiento_grafo
                self.desplazamiento_grafo = (ax + dx * paso, ay + dy * paso)
            self._mostrar_mapa(self.ruta_actual)

        for texto, accion in [
            ("+", lambda: cmd(1.25)), ("-", lambda: cmd(1 / 1.25)), ("Centrar", lambda: cmd(1, centrar=True)),
            ("<", lambda: cmd(1, -1)), (">", lambda: cmd(1, 1)), ("^", lambda: cmd(1, 0, 1)), ("v", lambda: cmd(1, 0, -1)),
        ]:
            self._boton(controles, texto, accion).pack(side="left", padx=3)

        self.panel_mapa = tk.Frame(parent, bg=COLOR_PANEL)
        self.panel_mapa.grid(row=1, column=0, sticky="nsew", padx=14, pady=(0, 14))

    def calcular(self):
        origen, destino = self.combo_origen.get(), self.combo_destino.get()
        if not origen or not destino:
            return messagebox.showerror("Datos incompletos", "Selecciona origen y destino.")
        try:
            peso = float(self.entry_peso.get())
            if peso <= 0:
                raise ValueError()
        except ValueError:
            return messagebox.showerror("Peso inválido", "El peso debe ser mayor a cero.")

        try:
            res = self._api("/ruta", {"origen": origen, "destino": destino}, timeout=5.0)
            if res.get("error"):
                raise RuntimeError(res["error"])
            km, ruta = res["km"], res["ruta"]
        except Exception as e:
            return messagebox.showerror("Error de API", f"No se pudo calcular la ruta: {e}")
        if not ruta or km is None:
            return messagebox.showerror("Sin ruta", "No existe una ruta viable.")

        c_base, c_km, c_libra, costo_total, precio_final = config_tarifas.calcular_factura(km, peso)
        margen = config_tarifas.obtener()["MARGEN_UTILIDAD"]
        nota_local = ""
        if origen == destino:
            nota_local = "\nServicio local: no hay recorrido entre municipios, solo se cobra base y peso."
        self.lbl_ruta.config(text=" → ".join(ruta))
        self.lbl_km.config(text=f"{km} km")
        self.lbl_costo_total.config(text=(
            f"  Q {c_base:.2f} (Costo Fijo Base)\n"
            f"+ Q {c_km * km:.2f} (Distancia: {km} km × Q {c_km:.2f})\n"
            f"+ Q {c_libra * peso:.2f} (Peso: {peso} lb × Q {c_libra:.2f})\n"
            f"────────────────────────────\n"
            f"  Q {costo_total:.2f} (Subtotal Costo Operativo)\n"
            f"+ Q {costo_total * margen:.2f} (Utilidad {margen * 100:.0f}%)"
            f"{nota_local}"
        ))
        self.lbl_precio_final.config(text=f"Q {precio_final:.2f}")
        self.ruta_actual = ruta
        self._mostrar_mapa(ruta)

    def actualizar_grafo_por_seleccion(self, event=None):
        origen, destino = self.combo_origen.get(), self.combo_destino.get()
        if not origen and not destino:
            ruta = []
        elif origen and destino and origen != destino:
            try:
                ruta = self._api("/ruta", {"origen": origen, "destino": destino}).get("ruta", [])
            except Exception:
                ruta = [origen, destino]
        else:
            ruta = [origen or destino]
        self.ruta_actual = ruta
        self._mostrar_mapa(ruta)

    def reiniciar_cotizacion(self):
        self.combo_origen.set("")
        self.combo_destino.set("")
        self.entry_peso.delete(0, tk.END)
        for lbl in (self.lbl_ruta, self.lbl_km, self.lbl_costo_total, self.lbl_precio_final):
            lbl.config(text="-")
        self.ruta_actual = []
        self.zoom_grafo, self.desplazamiento_grafo = 1.0, (0.0, 0.0)
        self._mostrar_mapa([])

    def _mostrar_mapa(self, ruta):
        if self.matriz is None or not self.municipios:
            return
        try:
            self.canvas_grafo = visualizador_grafo.mostrar_grafo_en_tk(
                self.panel_mapa, self.matriz, self.municipios, ruta, self.zoom_grafo, self.desplazamiento_grafo,
            )
            self._activar_arrastre_grafo()
        except Exception as e:
            for w in self.panel_mapa.winfo_children():
                w.destroy()
            tk.Label(self.panel_mapa, text=f"Error al dibujar el mapa: {e}", bg=COLOR_PANEL, fg=COLOR_ERROR,
                     font=("Segoe UI", 10, "bold")).pack(anchor="center", pady=20)

    def _activar_arrastre_grafo(self):
        estado = {"inicio": None}

        def iniciar(event):
            if event.inaxes and event.xdata is not None and event.ydata is not None:
                estado["inicio"] = (event.xdata, event.ydata, event.inaxes.get_xlim(), event.inaxes.get_ylim())

        def arrastrar(event):
            if not estado["inicio"] or not event.inaxes or event.xdata is None or event.ydata is None:
                return
            ix, iy, lx, ly = estado["inicio"]
            event.inaxes.set_xlim(lx[0] + ix - event.xdata, lx[1] + ix - event.xdata)
            event.inaxes.set_ylim(ly[0] + iy - event.ydata, ly[1] + iy - event.ydata)
            self.desplazamiento_grafo = (sum(event.inaxes.get_xlim()) / 2, sum(event.inaxes.get_ylim()) / 2)
            self.canvas_grafo.draw_idle()

        self.canvas_grafo.mpl_connect("button_press_event", iniciar)
        self.canvas_grafo.mpl_connect("motion_notify_event", arrastrar)
        self.canvas_grafo.mpl_connect("button_release_event", lambda ev: estado.update(inicio=None))

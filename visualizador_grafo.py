import html
import re
import unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np


SIN_CONEXION = 999
RUTA_DRAWIO = Path.home() / "OneDrive" / "Desktop" / "Prograterminado (1)(10).drawio"
ALIAS_DRAWIO = {
    "CIUDAD DE GUATEMALA": "GUATEMALA",
    "SACATEPEQUEZ ANTIGUA GUATEMALA": "LA ANTIGUA GUATEMALA",
    "SAN RAIMUNDO": "SAN RAYMUNDO",
    "CHUARRAMCHO": "CHUARRANCHO",
    "COMALAPA": "SAN JUAN COMALAPA",
    "TECPAN": "TECPAN GUATEMALA",
}


def _normalizar(texto):
    texto = html.unescape(str(texto))
    texto = re.sub(r"<[^>]+>", " ", texto)
    texto = re.sub(r"^\s*\d+\.?\s*", "", texto)
    texto = " ".join(texto.upper().split())
    texto = unicodedata.normalize("NFD", texto)
    return "".join(letra for letra in texto if unicodedata.category(letra) != "Mn")


def _tokens_nombre(texto):
    palabras_ignoradas = {"DE", "DEL", "LA", "LAS", "EL", "LOS", "Y"}
    return {
        palabra
        for palabra in _normalizar(texto).split()
        if len(palabra) > 2 and palabra not in palabras_ignoradas
    }


def cargar_posiciones_drawio(municipios, ruta_drawio=RUTA_DRAWIO):
    """
    Lee el archivo de diagrams.net y extrae coordenadas de los nodos.

    Si el archivo no existe o no coincide con todos los municipios, devuelve
    solamente las posiciones que pudo reconocer. El resto se acomoda con
    NetworkX al momento de dibujar.
    """
    ruta_drawio = Path(ruta_drawio)
    if not ruta_drawio.exists():
        return {}

    posiciones = {}
    municipios_normalizados = {_normalizar(municipio): municipio for municipio in municipios}

    try:
        raiz = ET.parse(ruta_drawio).getroot()
    except ET.ParseError:
        return {}

    for celda in raiz.iter("mxCell"):
        if celda.get("vertex") != "1":
            continue

        valor = _normalizar(celda.get("value", ""))
        if not valor:
            continue

        municipio_encontrado = municipios_normalizados.get(valor)
        if municipio_encontrado is None:
            alias = ALIAS_DRAWIO.get(valor)
            if alias in municipios:
                municipio_encontrado = alias

        if municipio_encontrado is None:
            tokens_valor = _tokens_nombre(valor)
            candidatos = []

            for municipio_original in municipios:
                tokens_municipio = _tokens_nombre(municipio_original)
                if not tokens_municipio:
                    continue

                coincidencias = len(tokens_valor & tokens_municipio)
                puntaje = coincidencias / len(tokens_municipio)
                candidatos.append((puntaje, coincidencias, len(tokens_municipio), municipio_original))

            candidatos.sort(reverse=True)
            mejor_puntaje, coincidencias, _, mejor_municipio = candidatos[0]
            if mejor_puntaje >= 0.66 and coincidencias >= 2:
                municipio_encontrado = mejor_municipio

        if municipio_encontrado is None:
            continue

        geometria = celda.find("mxGeometry")
        if geometria is None:
            continue

        x = float(geometria.get("x", 0))
        y = float(geometria.get("y", 0))
        ancho = float(geometria.get("width", 0))
        alto = float(geometria.get("height", 0))
        posiciones[municipio_encontrado] = (x + ancho / 2, -(y + alto / 2))

    return posiciones


def construir_grafo(matriz_distancias, municipios, sin_conexion=SIN_CONEXION):
    """
    Convierte la matriz de distancias en un grafo de NetworkX.
    """
    try:
        import networkx as nx
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "Falta instalar NetworkX. Usa: pip install networkx matplotlib"
        ) from exc

    grafo = nx.Graph()
    grafo.add_nodes_from(municipios)
    matriz = np.array(matriz_distancias, dtype=float)

    for i, origen in enumerate(municipios):
        for j in range(i + 1, len(municipios)):
            distancia = matriz[i][j]
            if np.isfinite(distancia) and 0 < distancia < sin_conexion:
                grafo.add_edge(origen, municipios[j], weight=distancia)

    return grafo


def _normalizar_posiciones(posiciones):
    if not posiciones:
        return {}

    xs = [punto[0] for punto in posiciones.values()]
    ys = [punto[1] for punto in posiciones.values()]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    rango_x = max(max_x - min_x, 1)
    rango_y = max(max_y - min_y, 1)

    return {
        nodo: (
            ((x - min_x) / rango_x) * 2 - 1,
            ((y - min_y) / rango_y) * 2 - 1,
        )
        for nodo, (x, y) in posiciones.items()
    }


def _obtener_posiciones(grafo, municipios, ruta_drawio=RUTA_DRAWIO):
    import networkx as nx

    posiciones = _normalizar_posiciones(cargar_posiciones_drawio(municipios, ruta_drawio))
    fijos = [nodo for nodo in grafo.nodes if nodo in posiciones]

    if fijos:
        return nx.spring_layout(
            grafo,
            pos=posiciones,
            fixed=fijos,
            seed=7,
            k=0.45,
            iterations=100,
            weight="weight",
        )

    return nx.spring_layout(grafo, seed=7, k=0.85, iterations=100, weight="weight")


def _pares_ruta(ruta):
    return {tuple(sorted((ruta[i], ruta[i + 1]))) for i in range(len(ruta) - 1)}


def _coincidir_ruta_con_municipios(ruta_optima, municipios):
    municipios_por_nombre = {_normalizar(municipio): municipio for municipio in municipios}
    ruta_corregida = []

    for nodo in ruta_optima or []:
        nodo_normalizado = _normalizar(nodo)
        if nodo_normalizado in municipios_por_nombre:
            ruta_corregida.append(municipios_por_nombre[nodo_normalizado])
            continue

        coincidencia = next(
            (
                municipio_original
                for municipio_normalizado, municipio_original in municipios_por_nombre.items()
                if nodo_normalizado in municipio_normalizado
                or municipio_normalizado in nodo_normalizado
            ),
            nodo,
        )
        ruta_corregida.append(coincidencia)

    return ruta_corregida


def _preparar_grafo_visible(grafo_completo, ruta_optima):
    if len(ruta_optima) < 2:
        return grafo_completo.copy()

    grafo_visible = grafo_completo.__class__()
    grafo_visible.add_nodes_from(ruta_optima)

    for origen, destino in zip(ruta_optima, ruta_optima[1:]):
        if grafo_completo.has_edge(origen, destino):
            grafo_visible.add_edge(origen, destino, **grafo_completo[origen][destino])

    return grafo_visible


def _nombre_corto(municipio):
    reemplazos = {
        "Sacatepequez": "Sac.",
        "Guatemala": "Guate.",
        "Santa": "Sta.",
        "Santo": "Sto.",
        "San ": "S. ",
    }
    nombre = municipio.title()
    for texto, reemplazo in reemplazos.items():
        nombre = nombre.replace(texto, reemplazo)
    return nombre


def crear_figura_grafo(
    matriz_distancias,
    municipios,
    ruta_optima=None,
    ruta_drawio=RUTA_DRAWIO,
    tamano_figura=(12, 7.2),
    zoom=1.0,
    desplazamiento=(0.0, 0.0),
):
    """
    Crea una figura de Matplotlib con el grafo completo y la ruta resaltada.
    """
    try:
        import matplotlib.pyplot as plt
        import networkx as nx
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "Falta instalar Matplotlib/NetworkX. Usa: pip install matplotlib networkx"
        ) from exc

    ruta_optima = _coincidir_ruta_con_municipios(ruta_optima, municipios)
    grafo_completo = construir_grafo(matriz_distancias, municipios)
    grafo = grafo_completo
    posiciones_completas = _obtener_posiciones(grafo_completo, municipios, ruta_drawio)
    posiciones = {nodo: posiciones_completas[nodo] for nodo in grafo.nodes()}

    figura, eje = plt.subplots(figsize=tamano_figura, dpi=100)
    figura.patch.set_facecolor("#181818")
    eje.set_facecolor("#181818")
    eje.set_title(
        "Grafo completo y ruta optima",
        color="#f8fafc",
        fontsize=13,
        fontweight="bold",
        pad=12,
    )
    eje.axis("off")

    aristas_ruta = _pares_ruta(ruta_optima)
    aristas_base = [
        (u, v)
        for u, v in grafo.edges()
        if tuple(sorted((u, v))) not in aristas_ruta
    ]
    aristas_resaltadas = [
        (u, v)
        for u, v in grafo.edges()
        if tuple(sorted((u, v))) in aristas_ruta
    ]

    colores_nodos = ["#16a34a" if nodo in ruta_optima else "#181818" for nodo in grafo.nodes()]
    bordes_nodos = ["#bbf7d0" if nodo in ruta_optima else "#e5e7eb" for nodo in grafo.nodes()]

    nx.draw_networkx_edges(
        grafo,
        posiciones,
        edgelist=aristas_base,
        edge_color="#6b7280",
        width=1,
        alpha=0.7,
        ax=eje,
    )

    nx.draw_networkx_edges(
        grafo,
        posiciones,
        edgelist=aristas_resaltadas,
        edge_color="#dc2626",
        width=4.5,
        ax=eje,
    )
    tamanos_nodos = [760 if nodo in ruta_optima else 260 for nodo in grafo.nodes()]

    nx.draw_networkx_nodes(
        grafo,
        posiciones,
        node_color=colores_nodos,
        edgecolors=bordes_nodos,
        linewidths=1.3,
        node_size=tamanos_nodos,
        ax=eje,
    )

    etiquetas_base = {
        nodo: _nombre_corto(nodo)
        for nodo in grafo.nodes()
        if nodo not in ruta_optima
    }
    nx.draw_networkx_labels(
        grafo,
        posiciones,
        labels=etiquetas_base,
        font_size=5.2,
        font_family="Segoe UI",
        font_color="#f8fafc",
        ax=eje,
    )

    etiquetas_ruta = {nodo: _nombre_corto(nodo) for nodo in grafo.nodes() if nodo in ruta_optima}
    nx.draw_networkx_labels(
        grafo,
        posiciones,
        labels=etiquetas_ruta,
        font_size=7.5,
        font_family="Segoe UI",
        font_weight="bold",
        font_color="#ffffff",
        ax=eje,
    )

    etiquetas_pesos_base = {
        (u, v): f"{datos['weight']:g} km"
        for u, v, datos in grafo.edges(data=True)
        if tuple(sorted((u, v))) not in aristas_ruta
    }
    nx.draw_networkx_edge_labels(
        grafo,
        posiciones,
        edge_labels=etiquetas_pesos_base,
        font_size=4.5,
        font_color="#e5e7eb",
        label_pos=0.5,
        rotate=True,
        ax=eje,
    )

    etiquetas_pesos_ruta = {
        (u, v): f"{datos['weight']:g} km"
        for u, v, datos in grafo.edges(data=True)
        if tuple(sorted((u, v))) in aristas_ruta
    }
    nx.draw_networkx_edge_labels(
        grafo,
        posiciones,
        edge_labels=etiquetas_pesos_ruta,
        font_size=9,
        font_color="#dc2626",
        bbox={
            "boxstyle": "round,pad=0.25",
            "facecolor": "#ffffff",
            "edgecolor": "#fecaca",
            "linewidth": 0.8,
            "alpha": 0.95,
        },
        label_pos=0.5,
        rotate=True,
        ax=eje,
    )

    eje.margins(0.08)
    zoom = max(float(zoom), 0.35)
    centro_x, centro_y = desplazamiento
    eje.set_xlim(centro_x - 1.15 / zoom, centro_x + 1.15 / zoom)
    eje.set_ylim(centro_y - 1.15 / zoom, centro_y + 1.15 / zoom)
    eje.set_aspect("auto")
    x_min, x_max = eje.get_xlim()
    y_min, y_max = eje.get_ylim()
    for x in np.arange(-1.4, 1.45, 0.05):
        eje.axvline(x, color="#2f3338", linewidth=0.35, zorder=0)
    for y in np.arange(-1.4, 1.45, 0.05):
        eje.axhline(y, color="#2f3338", linewidth=0.35, zorder=0)
    for x in np.arange(-1.4, 1.45, 0.25):
        eje.axvline(x, color="#40454c", linewidth=0.6, zorder=0)
    for y in np.arange(-1.4, 1.45, 0.25):
        eje.axhline(y, color="#40454c", linewidth=0.6, zorder=0)
    eje.set_xlim(x_min, x_max)
    eje.set_ylim(y_min, y_max)
    figura.tight_layout(pad=1.5)
    return figura


def mostrar_grafo_en_tk(
    contenedor,
    matriz_distancias,
    municipios,
    ruta_optima,
    zoom=1.0,
    desplazamiento=(0.0, 0.0),
):
    """
    Inserta el mapa dentro de un contenedor Tkinter.
    """
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

    for widget in contenedor.winfo_children():
        widget.destroy()

    contenedor.update_idletasks()
    ancho = max(contenedor.winfo_width(), 900)
    alto = max(contenedor.winfo_height(), 520)
    figura = crear_figura_grafo(
        matriz_distancias,
        municipios,
        ruta_optima,
        tamano_figura=(ancho / 100, alto / 100),
        zoom=zoom,
        desplazamiento=desplazamiento,
    )
    canvas = FigureCanvasTkAgg(figura, master=contenedor)
    canvas.draw()
    widget_canvas = canvas.get_tk_widget()
    widget_canvas.pack(fill="both", expand=True)
    return canvas


def dibujar_grafo(matriz_distancias, municipios, ruta_optima=None):
    """
    Funcion simple para pruebas: abre una ventana independiente con el grafo.
    """
    import matplotlib.pyplot as plt

    figura = crear_figura_grafo(matriz_distancias, municipios, ruta_optima)
    figura.show()
    plt.show()

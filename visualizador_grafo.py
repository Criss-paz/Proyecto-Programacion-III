import html
import re
import unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx


DRAWIO = Path(__file__).with_name("grafo.drawio")
ALIAS = {
    "CIUDAD DE GUATEMALA": "GUATEMALA",
    "SACATEPEQUEZ ANTIGUA GUATEMALA": "LA ANTIGUA GUATEMALA",
    "COMALAPA": "SAN JUAN COMALAPA",
    "TECPAN": "TECPAN GUATEMALA",
    "SAN RAIMUNDO": "SAN RAYMUNDO",
    "CHUARRAMCHO": "CHUARRANCHO",
    "SAN ANDREZ IZTAPA": "SAN ANDRES ITZAPA",
    "SAN PEDRO AYAPUC": "SAN PEDRO AYAMPUC",
}


def normalizar(texto):
    texto = html.unescape(texto or "")
    texto = re.sub(r"<[^>]+>|\d+[\.\-]?", " ", texto).replace("\xa0", " ")
    texto = re.sub(r"\s+", " ", texto).strip().upper()
    texto = "".join(c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn")
    return ALIAS.get(texto, texto)


def posiciones_drawio(municipios):
    if not DRAWIO.exists():
        return {}

    nombres = {normalizar(m): m for m in municipios}
    posiciones = {}

    try:
        celdas = ET.parse(DRAWIO).getroot().iter("mxCell")
    except ET.ParseError:
        return {}

    for celda in celdas:
        nombre = nombres.get(normalizar(celda.get("value")))
        geo = celda.find("mxGeometry")
        if nombre and geo is not None and celda.get("vertex") == "1" and "ellipse" in celda.get("style", ""):
            x = float(geo.get("x", 0)) + float(geo.get("width", 0)) / 2
            y = float(geo.get("y", 0)) + float(geo.get("height", 0)) / 2
            posiciones[nombre] = (x, -y)

    return posiciones


def crear_grafo(municipios, matriz):
    grafo = nx.Graph()
    grafo.add_nodes_from(municipios)

    for i, origen in enumerate(municipios):
        for j, destino in enumerate(municipios[i + 1:], start=i + 1):
            km = float(matriz[i][j])
            if 0 < km < 990:
                grafo.add_edge(origen, destino, weight=km)

    return grafo


def dibujar_mapa(municipios, matriz, ruta_optima=None):
    ruta = ruta_optima or []
    grafo = crear_grafo(municipios, matriz)
    posiciones = posiciones_drawio(municipios)
    if len(posiciones) < len(municipios):
        automaticas = nx.spring_layout(grafo, seed=42, k=0.9)
        for municipio in municipios:
            posiciones.setdefault(municipio, automaticas[municipio])

    aristas_ruta = set(zip(ruta, ruta[1:])) | set(zip(ruta[1:], ruta))
    aristas_normales = [a for a in grafo.edges if a not in aristas_ruta]
    aristas_destacadas = [a for a in grafo.edges if a in aristas_ruta]
    etiquetas = {(a, b): f"{d['weight']:.2f} km" for a, b, d in grafo.edges(data=True)}

    plt.figure(figsize=(15, 8))
    plt.title("Mapa de Rutas - Envios Rapidos GT")
    nx.draw_networkx_edges(grafo, posiciones, edgelist=aristas_normales, edge_color="#cbd5e1", arrows=False)
    nx.draw_networkx_edges(grafo, posiciones, edgelist=aristas_destacadas, edge_color="red", width=4, arrows=False)
    nx.draw_networkx_nodes(grafo, posiciones, node_color=["red" if n in ruta else "#94a3b8" for n in grafo.nodes])
    nx.draw_networkx_labels(grafo, posiciones, font_size=6)
    nx.draw_networkx_edge_labels(
        grafo,
        posiciones,
        edge_labels={a: etiquetas[a] for a in aristas_normales},
        font_size=5,
    )
    nx.draw_networkx_edge_labels(
        grafo,
        posiciones,
        edge_labels={a: etiquetas[a] for a in aristas_destacadas},
        font_size=8,
        font_color="white",
        bbox={"facecolor": "red", "edgecolor": "none", "pad": 0.25},
    )
    plt.axis("off")
    plt.tight_layout()
    plt.show(block=False)

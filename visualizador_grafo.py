import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from pathlib import Path
import html
import re
import unicodedata
import xml.etree.ElementTree as ET


RUTA_DRAWIO = Path(__file__).resolve().parent / "grafo.drawio"


ALIAS_DRAWIO = {
    "CIUDAD DE GUATEMALA": "GUATEMALA",
    "SACATEPEQUEZ ANTIGUA GUATEMALA": "LA ANTIGUA GUATEMALA",
    "COMALAPA": "SAN JUAN COMALAPA",
    "TECPAN": "TECPAN GUATEMALA",
    "SAN RAIMUNDO": "SAN RAYMUNDO",
    "CHUARRAMCHO": "CHUARRANCHO",
    "SAN ANDREZ IZTAPA": "SAN ANDRES ITZAPA",
    "SAN PEDRO AYAPUC": "SAN PEDRO AYAMPUC",
}


def _normalizar_nombre(texto):
    texto = html.unescape(texto or "")
    texto = re.sub(r"<[^>]+>", " ", texto)
    texto = texto.replace("\xa0", " ")
    texto = re.sub(r"^\s*\d+\s*[\.\-]?\s*", "", texto)
    texto = re.sub(r"\s+", " ", texto).strip().upper()
    texto = "".join(
        c for c in unicodedata.normalize("NFD", texto)
        if unicodedata.category(c) != "Mn"
    )
    return ALIAS_DRAWIO.get(texto, texto)


def _posiciones_desde_drawio(municipios):
    if not RUTA_DRAWIO.exists():
        return {}

    municipios_por_nombre = {_normalizar_nombre(m): m for m in municipios}
    posiciones = {}

    try:
        raiz = ET.parse(RUTA_DRAWIO).getroot()
    except ET.ParseError:
        return {}

    for celda in raiz.iter("mxCell"):
        if celda.get("vertex") != "1" or celda.get("connectable") == "0":
            continue
        if "ellipse" not in celda.get("style", ""):
            continue

        municipio = municipios_por_nombre.get(_normalizar_nombre(celda.get("value", "")))
        if not municipio:
            continue

        geometria = celda.find("mxGeometry")
        if geometria is None:
            continue

        x = float(geometria.get("x", 0)) + float(geometria.get("width", 0)) / 2
        y = float(geometria.get("y", 0)) + float(geometria.get("height", 0)) / 2
        posiciones[municipio] = (x, -y)

    return posiciones

def dibujar_mapa(municipios, matriz, ruta_optima=None, ax=None):
    ruta_optima = ruta_optima or []
    G = nx.Graph()
    G.add_nodes_from(municipios)
    
    m = np.array(matriz, dtype=float)
    n = len(municipios)
    
    for i in range(n):
        for j in range(i + 1, n):
            d = m[i][j]
            if np.isfinite(d) and 0 < d < 990:
                G.add_edge(municipios[i], municipios[j], weight=d)

    aristas_ruta = []
    if ruta_optima and len(ruta_optima) > 1:
        for i in range(len(ruta_optima) - 1):
            aristas_ruta.append((ruta_optima[i], ruta_optima[i+1]))
            aristas_ruta.append((ruta_optima[i+1], ruta_optima[i]))

    aristas_base = [e for e in G.edges() if e not in aristas_ruta and (e[1], e[0]) not in aristas_ruta]
    aristas_destacadas = [e for e in G.edges() if e in aristas_ruta or (e[1], e[0]) in aristas_ruta]

    color_nodos = ["#dc2626" if nodo in ruta_optima else "#94a3b8" for nodo in G.nodes()]
    tamano_nodos = [500 if nodo in ruta_optima else 50 for nodo in G.nodes()]

    mostrar_ventana = ax is None
    if mostrar_ventana:
        _, ax = plt.subplots(figsize=(16, 9))
    else:
        ax.clear()

    ax.set_title("Mapa de Rutas - Envios Rapidos GT", fontsize=13, fontweight="bold", pad=10)
    
    posiciones = _posiciones_desde_drawio(municipios)
    if len(posiciones) < len(municipios):
        faltantes = [nodo for nodo in municipios if nodo not in posiciones]
        for indice, nodo in enumerate(faltantes):
            vecinos = [vecino for vecino in G.neighbors(nodo) if vecino in posiciones]
            if vecinos:
                x = sum(posiciones[vecino][0] for vecino in vecinos) / len(vecinos)
                y = sum(posiciones[vecino][1] for vecino in vecinos) / len(vecinos)
                posiciones[nodo] = (x - 120 + (indice * 30), y - 80)

        faltantes = [nodo for nodo in municipios if nodo not in posiciones]
        if faltantes:
            posiciones_extra = nx.spring_layout(G.subgraph(faltantes), k=8.0, weight=None, seed=42, iterations=500)
            posiciones.update(posiciones_extra)
    
    nx.draw_networkx_nodes(G, posiciones, ax=ax, node_color=color_nodos, node_size=tamano_nodos, edgecolors="#0f172a", linewidths=1.5)
    nx.draw_networkx_edges(G, posiciones, ax=ax, edgelist=aristas_base, edge_color="#cbd5e1", width=1.0)
    nx.draw_networkx_edges(G, posiciones, ax=ax, edgelist=aristas_destacadas, edge_color="#dc2626", width=4.5)
    
    valores_y = [coords[1] for coords in posiciones.values()]
    offset_texto = max((max(valores_y) - min(valores_y)) * 0.018, 10) if valores_y else 10
    posiciones_textos = {nodo: (coords[0], coords[1] + offset_texto) for nodo, coords in posiciones.items()}

    etiquetas_base = {nodo: nodo for nodo in G.nodes() if nodo not in ruta_optima}
    nx.draw_networkx_labels(G, posiciones_textos, ax=ax, labels=etiquetas_base, font_size=5, font_color="#475569", bbox=dict(facecolor="white", edgecolor="none", alpha=0.8, pad=0.1))

    etiquetas_km_base = {(u, v): f"{d['weight']} km" for u, v, d in G.edges(data=True) if (u, v) not in aristas_destacadas and (v, u) not in aristas_destacadas}
    nx.draw_networkx_edge_labels(G, posiciones, ax=ax, edge_labels=etiquetas_km_base, font_size=5, font_color="#94a3b8", bbox=dict(facecolor="white", edgecolor="none", alpha=0.8, pad=0.1))

    etiquetas_ruta = {nodo: nodo for nodo in G.nodes() if nodo in ruta_optima}
    nx.draw_networkx_labels(G, posiciones_textos, ax=ax, labels=etiquetas_ruta, font_size=10, font_weight="bold", font_color="#000000", bbox=dict(facecolor="white", edgecolor="none", alpha=0.9, pad=0.3))
    
    etiquetas_km_ruta = {(u, v): f"{d['weight']} km" for u, v, d in G.edges(data=True) if (u, v) in aristas_destacadas or (v, u) in aristas_destacadas}
    nx.draw_networkx_edge_labels(G, posiciones, ax=ax, edge_labels=etiquetas_km_ruta, font_size=9, font_weight="bold", font_color="#ffffff", bbox=dict(facecolor="#dc2626", edgecolor="none", alpha=1.0, pad=0.3))
    
    ax.margins(0.08)
    ax.axis("off")

    if mostrar_ventana:
        plt.tight_layout()
        plt.show()

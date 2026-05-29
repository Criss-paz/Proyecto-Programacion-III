"""Dibuja el grafo municipal con matplotlib y networkx."""

import html, re, unicodedata, xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np

SIN_CONEXION = 999999
_cache_posiciones = None
RUTA_DRAWIO = Path(__file__).resolve().parent.parent / "datos" / "grafo.drawio"
ALIAS_DRAWIO = {
    "CIUDAD DE GUATEMALA": "GUATEMALA", "SACATEPEQUEZ ANTIGUA GUATEMALA": "LA ANTIGUA GUATEMALA",
    "SAN RAIMUNDO": "SAN RAYMUNDO", "CHUARRAMCHO": "CHUARRANCHO",
    "COMALAPA": "SAN JUAN COMALAPA", "TECPAN": "TECPAN GUATEMALA",
}


def _normalizar(t):
    t = html.unescape(str(t))
    t = re.sub(r"<[^>]+>", " ", t)
    t = re.sub(r"^\s*\d+\.?\s*", "", t)
    t = " ".join(t.upper().split())
    return "".join(c for c in unicodedata.normalize("NFD", t) if unicodedata.category(c) != "Mn")


def cargar_posiciones_drawio(municipios, ruta_drawio=RUTA_DRAWIO):
    if not Path(ruta_drawio).exists():
        return {}
    pos, m_norm = {}, {_normalizar(m): m for m in municipios}
    try:
        raiz = ET.parse(ruta_drawio).getroot()
    except Exception:
        return {}
    for celda in raiz.iter("mxCell"):
        if celda.get("vertex") != "1":
            continue
        val = _normalizar(celda.get("value", ""))
        if not val:
            continue
        match = m_norm.get(val) or ALIAS_DRAWIO.get(val)
        if not match:
            match = next((o for n, o in m_norm.items() if val in n or n in val), None)
        if match in municipios:
            geom = celda.find("mxGeometry")
            if geom is not None:
                x, y = float(geom.get("x", 0)), float(geom.get("y", 0))
                w, h = float(geom.get("width", 0)), float(geom.get("height", 0))
                pos[match] = (x + w / 2, -(y + h / 2))
    return pos


def construir_grafo(matriz, municipios, sin_conexion=SIN_CONEXION):
    import networkx as nx
    g = nx.Graph()
    g.add_nodes_from(municipios)
    m = np.array(matriz, dtype=float)
    for i, o in enumerate(municipios):
        for j in range(i + 1, len(municipios)):
            d = m[i][j]
            if np.isfinite(d) and 0 < d < sin_conexion:
                g.add_edge(o, municipios[j], weight=d)
    return g


def _normalizar_posiciones(pos):
    if not pos:
        return {}
    xs, ys = [p[0] for p in pos.values()], [p[1] for p in pos.values()]
    min_x, max_x, min_y, max_y = min(xs), max(xs), min(ys), max(ys)
    rx, ry = max(max_x - min_x, 1), max(max_y - min_y, 1)
    return {n: (((x - min_x) / rx) * 2 - 1, ((y - min_y) / ry) * 2 - 1) for n, (x, y) in pos.items()}


def _obtener_posiciones(g, municipios, ruta_drawio=RUTA_DRAWIO):
    global _cache_posiciones
    import networkx as nx
    if _cache_posiciones is not None:
        return _cache_posiciones
    pos = _normalizar_posiciones(cargar_posiciones_drawio(municipios, ruta_drawio))
    fijos = [n for n in g.nodes if n in pos]
    _cache_posiciones = (
        nx.spring_layout(g, pos=pos, fixed=fijos, seed=7, k=0.45, iterations=100, weight="weight")
        if fijos else nx.spring_layout(g, seed=7, k=0.85, iterations=100, weight="weight")
    )
    return _cache_posiciones


def _pares_ruta(ruta):
    return {tuple(sorted((ruta[i], ruta[i + 1]))) for i in range(len(ruta) - 1)}


def _coincidir_ruta_con_municipios(ruta, municipios):
    m_norm = {_normalizar(m): m for m in municipios}
    res = []
    for n in ruta or []:
        norm = _normalizar(n)
        res.append(m_norm.get(norm) or next((o for nm, o in m_norm.items() if norm in nm or nm in norm), n))
    return res


def _nombre_corto(m):
    rep = {"Sacatepequez": "Sac.", "Guatemala": "Guate.", "Santa": "Sta.", "Santo": "Sto.", "San ": "S. "}
    n = m.title()
    for k, v in rep.items():
        n = n.replace(k, v)
    return n


def crear_figura_grafo(matriz, municipios, ruta_optima=None, tamano_figura=(12, 7.2), zoom=1.0, desv=(0.0, 0.0)):
    import matplotlib.pyplot as plt
    import networkx as nx

    ruta_optima = _coincidir_ruta_con_municipios(ruta_optima, municipios)
    g = construir_grafo(matriz, municipios)
    pos = {n: p for n, p in _obtener_posiciones(g, municipios).items() if n in g}

    fig, ax = plt.subplots(figsize=tamano_figura, dpi=100)
    fig.patch.set_facecolor("#ffffff")
    ax.set_facecolor("#ffffff")
    ax.axis("off")

    ar_ruta = _pares_ruta(ruta_optima)
    ebase = [e for e in g.edges() if tuple(sorted(e)) not in ar_ruta]
    eruta = [e for e in g.edges() if tuple(sorted(e)) in ar_ruta]

    nx.draw_networkx_edges(g, pos, edgelist=ebase, edge_color="#cbd5e1", width=0.9, alpha=0.75, ax=ax)
    nx.draw_networkx_edges(g, pos, edgelist=eruta, edge_color="#ef4444", width=3.6, ax=ax)

    colores = ["#2563eb" if n in ruta_optima else "#f8fafc" for n in g.nodes()]
    bordes = ["#1d4ed8" if n in ruta_optima else "#cbd5e1" for n in g.nodes()]
    tamanos = [760 if n in ruta_optima else 260 for n in g.nodes()]
    nx.draw_networkx_nodes(g, pos, node_color=colores, edgecolors=bordes, linewidths=1.3, node_size=tamanos, ax=ax)

    lbl_base = {n: _nombre_corto(n) for n in g.nodes() if n not in ruta_optima}
    lbl_ruta = {n: _nombre_corto(n) for n in g.nodes() if n in ruta_optima}
    nx.draw_networkx_labels(g, pos, labels=lbl_base, font_size=5.2, font_family="Segoe UI", font_color="#334155", ax=ax)
    nx.draw_networkx_labels(g, pos, labels=lbl_ruta, font_size=7.5, font_family="Segoe UI", font_weight="bold", font_color="#ffffff", ax=ax)

    def etiquetas(en_ruta):
        return {(u, v): f"{d['weight']:g} km" for u, v, d in g.edges(data=True) if (tuple(sorted((u, v))) in ar_ruta) == en_ruta}

    nx.draw_networkx_edge_labels(g, pos, edge_labels=etiquetas(False), font_size=4.5, font_color="#94a3b8", rotate=True, ax=ax)
    nx.draw_networkx_edge_labels(g, pos, edge_labels=etiquetas(True), font_size=9, font_color="#dc2626",
        bbox={"boxstyle": "round,pad=0.25", "facecolor": "#ffffff", "edgecolor": "#fecaca", "linewidth": 0.8, "alpha": 0.95}, rotate=True, ax=ax)

    ax.margins(0.08)
    zoom = max(float(zoom), 0.35)
    ax.set_xlim(desv[0] - 1.15 / zoom, desv[0] + 1.15 / zoom)
    ax.set_ylim(desv[1] - 1.15 / zoom, desv[1] + 1.15 / zoom)
    return fig


def mostrar_grafo_en_tk(contenedor, matriz, municipios, ruta_optima, zoom=1.0, desv=(0.0, 0.0)):
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    for w in contenedor.winfo_children():
        w.destroy()
    contenedor.update_idletasks()
    fig = crear_figura_grafo(
        matriz, municipios, ruta_optima,
        tamano_figura=(max(contenedor.winfo_width(), 900) / 100, max(contenedor.winfo_height(), 520) / 100),
        zoom=zoom, desv=desv,
    )
    canvas = FigureCanvasTkAgg(fig, master=contenedor)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)
    return canvas

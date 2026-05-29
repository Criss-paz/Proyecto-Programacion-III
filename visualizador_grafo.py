import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

def dibujar_mapa(municipios, matriz, ruta_optima):
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

    plt.figure(figsize=(16, 9))
    plt.title("Mapa de Rutas - Envíos Rápidos GT (Cerrar para continuar)", fontsize=16, fontweight="bold", pad=15)
    
    posiciones = nx.spring_layout(G, k=8.0, weight=None, seed=42, iterations=1500) 
    
    nx.draw_networkx_nodes(G, posiciones, node_color=color_nodos, node_size=tamano_nodos, edgecolors="#0f172a", linewidths=1.5)
    nx.draw_networkx_edges(G, posiciones, edgelist=aristas_base, edge_color="#cbd5e1", width=1.0)
    nx.draw_networkx_edges(G, posiciones, edgelist=aristas_destacadas, edge_color="#dc2626", width=4.5)
    
    posiciones_textos = {nodo: (coords[0], coords[1] + 0.04) for nodo, coords in posiciones.items()}

    etiquetas_base = {nodo: nodo for nodo in G.nodes() if nodo not in ruta_optima}
    nx.draw_networkx_labels(G, posiciones_textos, labels=etiquetas_base, font_size=5, font_color="#475569", bbox=dict(facecolor="white", edgecolor="none", alpha=0.8, pad=0.1))

    etiquetas_km_base = {(u, v): f"{d['weight']} km" for u, v, d in G.edges(data=True) if (u, v) not in aristas_destacadas and (v, u) not in aristas_destacadas}
    nx.draw_networkx_edge_labels(G, posiciones, edge_labels=etiquetas_km_base, font_size=5, font_color="#94a3b8", bbox=dict(facecolor="white", edgecolor="none", alpha=0.8, pad=0.1))

    etiquetas_ruta = {nodo: nodo for nodo in G.nodes() if nodo in ruta_optima}
    nx.draw_networkx_labels(G, posiciones_textos, labels=etiquetas_ruta, font_size=10, font_weight="bold", font_color="#000000", bbox=dict(facecolor="white", edgecolor="none", alpha=0.9, pad=0.3))
    
    etiquetas_km_ruta = {(u, v): f"{d['weight']} km" for u, v, d in G.edges(data=True) if (u, v) in aristas_destacadas or (v, u) in aristas_destacadas}
    nx.draw_networkx_edge_labels(G, posiciones, edge_labels=etiquetas_km_ruta, font_size=9, font_weight="bold", font_color="#ffffff", bbox=dict(facecolor="#dc2626", edgecolor="none", alpha=1.0, pad=0.3))
    
    plt.margins(0.1)
    plt.tight_layout()
    plt.show()
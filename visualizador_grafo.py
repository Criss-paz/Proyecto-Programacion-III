import matplotlib.pyplot as plt
import networkx as nx

def dibujar_mapa(municipios, matriz, ruta_optima):
    G = nx.Graph()
    G.add_nodes_from(municipios)

    # Creamos las conexiones reales
    for i in range(len(municipios)):
        for j in range(i + 1, len(municipios)):
            km = float(matriz[i][j])
            if 0 < km < 990:
                G.add_edge(municipios[i], municipios[j], weight=km)

    # Identificamos los trazos de la ruta ganadora
    aristas_ruta = list(zip(ruta_optima, ruta_optima[1:]))
    aristas_destacadas = aristas_ruta + [(v, u) for u, v in aristas_ruta]

    colores_nodos = ["red" if n in ruta_optima else "#94a3b8" for n in G.nodes]
    colores_lineas = ["red" if e in aristas_destacadas else "#cbd5e1" for e in G.edges]
    grosor_lineas = [4 if e in aristas_destacadas else 1 for e in G.edges]

    plt.figure(figsize=(14, 8))
    plt.title("Mapa de Rutas - Envíos Rápidos GT", fontweight="bold")
    
    pos = nx.spring_layout(G, k=3.5, seed=42)
    
    nx.draw(G, pos, node_color=colores_nodos, edge_color=colores_lineas, width=grosor_lineas, 
            with_labels=True, node_size=300, font_size=7, font_weight="bold")
            
    etiquetas_km = {(u, v): f"{d['weight']} km" for u, v, d in G.edges(data=True) if (u,v) in aristas_destacadas}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=etiquetas_km, font_color="red")

    plt.tight_layout()
    plt.show(block=False)
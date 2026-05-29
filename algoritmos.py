import numpy as np

def aplicar_floyd_warshall(matriz):
    """Calcula distancias mínimas y la matriz de recorridos."""
    dist = np.array(matriz, dtype=float)
    dist[(dist == 999999) | np.isnan(dist)] = np.inf
    np.fill_diagonal(dist, 0)
    
    n = dist.shape[0]
    recorridos = np.full((n, n), -1, dtype=int)
    
    for i in range(n):
        for j in range(n):
            if i != j and np.isfinite(dist[i, j]):
                recorridos[i, j] = j

    # Algoritmo Core: Floyd-Warshall
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i, k] + dist[k, j] < dist[i, j]:
                    dist[i, j] = dist[i, k] + dist[k, j]
                    recorridos[i, j] = recorridos[i, k]
                    
    return dist, recorridos

def obtener_ruta_minima(recorridos, municipios, o, d):
    """Reconstruye el camino paso a paso."""
    if o == d: return [municipios[o]]
    if recorridos[o, d] == -1: return []
    
    ruta, actual = [municipios[o]], o
    while actual != d:
        actual = recorridos[actual, d]
        if actual == -1: return []
        ruta.append(municipios[actual])
    return ruta
"""Algoritmo Floyd-Warshall: distancia mínima y reconstrucción de ruta."""

import numpy as np

SIN_CONEXION = 999  # Valor del Excel cuando no hay camino directo


def aplicar_floyd_warshall(matriz_distancias, sin_conexion=SIN_CONEXION):
    """Calcula distancias mínimas entre todos los pares de nodos."""
    dist = np.array(matriz_distancias, dtype=float, copy=True)
    n = dist.shape[0]
    if dist.ndim != 2 or dist.shape[0] != dist.shape[1]:
        raise ValueError("La matriz de distancias debe ser cuadrada.")

    dist[(dist == sin_conexion) | np.isnan(dist)] = np.inf
    np.fill_diagonal(dist, 0)

    recorridos = np.full((n, n), -1, dtype=int)
    for i in range(n):
        for j in range(n):
            if i != j and np.isfinite(dist[i, j]):
                recorridos[i, j] = j

    for k in range(n):
        for i in range(n):
            for j in range(n):
                via = dist[i, k] + dist[k, j]
                if via < dist[i, j]:
                    dist[i, j] = via
                    recorridos[i, j] = recorridos[i, k]
    return dist, recorridos


def obtener_ruta_minima(recorridos, municipios, i, j):
    """Reconstruye la lista de municipios desde i hasta j."""
    if i == j:
        return [municipios[i]]
    if recorridos[i, j] == -1:
        return []
    ruta, actual = [municipios[i]], i
    while actual != j:
        actual = recorridos[actual, j]
        if actual == -1:
            return []
        ruta.append(municipios[actual])
    return ruta


def _indice(municipios, municipio):
    if isinstance(municipio, int) and 0 <= municipio < len(municipios):
        return municipio
    try:
        return municipios.index(municipio)
    except ValueError as e:
        raise ValueError(f"El municipio '{municipio}' no existe.") from e


def calcular_ruta_floyd(matriz_distancias, municipios, origen, destino):
    """Punto de entrada: devuelve (kilómetros, lista_de_municipios)."""
    i, j = _indice(municipios, origen), _indice(municipios, destino)
    dist, recorridos = aplicar_floyd_warshall(matriz_distancias)
    total = dist[i, j]
    if not np.isfinite(total):
        return float("inf"), []
    km = int(total) if float(total).is_integer() else float(total)
    return km, obtener_ruta_minima(recorridos, municipios, i, j)

"""Algoritmos para calcular rutas minimas."""

import numpy as np

SIN_CONEXION = 999


def aplicar_floyd_warshall(matriz_distancias, sin_conexion=SIN_CONEXION):
    """Devuelve la matriz de distancias minimas y la matriz de recorridos."""
    dist = _preparar_matriz(matriz_distancias, sin_conexion)
    recorridos = _crear_matriz_recorridos(dist)

    n = dist.shape[0]
    for k in range(n):
        for i in range(n):
            for j in range(n):
                nueva_distancia = dist[i, k] + dist[k, j]
                if nueva_distancia < dist[i, j]:
                    dist[i, j] = nueva_distancia
                    recorridos[i, j] = recorridos[i, k]
    return dist, recorridos


def calcular_ruta_floyd(matriz_distancias, municipios, origen, destino):
    """Devuelve los kilometros y la ruta entre origen y destino."""
    i = _indice(municipios, origen)
    j = _indice(municipios, destino)
    distancias, recorridos = aplicar_floyd_warshall(matriz_distancias)

    total = distancias[i, j]
    if not np.isfinite(total):
        return float("inf"), []
    return _formatear_km(total), obtener_ruta_minima(recorridos, municipios, i, j)


def obtener_ruta_minima(recorridos, municipios, origen_idx, destino_idx):
    """Reconstruye la ruta usando la matriz de recorridos de Floyd."""
    if origen_idx == destino_idx:
        return [municipios[origen_idx]]
    if recorridos[origen_idx, destino_idx] == -1:
        return []

    ruta = [municipios[origen_idx]]
    actual = origen_idx
    while actual != destino_idx:
        actual = recorridos[actual, destino_idx]
        if actual == -1:
            return []
        ruta.append(municipios[actual])
    return ruta


def _preparar_matriz(matriz_distancias, sin_conexion):
    matriz = np.array(matriz_distancias, dtype=float, copy=True)
    if matriz.ndim != 2 or matriz.shape[0] != matriz.shape[1]:
        raise ValueError("La matriz de distancias debe ser cuadrada.")

    matriz[(matriz == sin_conexion) | np.isnan(matriz)] = np.inf
    np.fill_diagonal(matriz, 0)
    return matriz


def _crear_matriz_recorridos(distancias):
    n = distancias.shape[0]
    recorridos = np.full((n, n), -1, dtype=int)
    for i in range(n):
        for j in range(n):
            if i != j and np.isfinite(distancias[i, j]):
                recorridos[i, j] = j
    return recorridos


def _indice(municipios, municipio):
    if isinstance(municipio, int) and 0 <= municipio < len(municipios):
        return municipio
    try:
        return municipios.index(municipio)
    except ValueError as e:
        raise ValueError(f"El municipio '{municipio}' no existe.") from e


def _formatear_km(valor):
    valor = round(float(valor), 2)
    return int(valor) if valor.is_integer() else valor

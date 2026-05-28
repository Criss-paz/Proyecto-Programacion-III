import numpy as np


SIN_CONEXION = 999


def aplicar_floyd_warshall(matriz_distancias, sin_conexion=SIN_CONEXION):
    """
    Calcula las rutas mas cortas entre todos los municipios.

    Recibe una matriz de Numpy donde el valor 999 significa que no hay
    conexion directa. Devuelve:
    1. distancias: matriz con los kilometros minimos entre cada par.
    2. recorridos: matriz para reconstruir el camino exacto.
    """
    distancias = np.array(matriz_distancias, dtype=float, copy=True)

    if distancias.ndim != 2 or distancias.shape[0] != distancias.shape[1]:
        raise ValueError("La matriz de distancias debe ser cuadrada.")

    n = distancias.shape[0]
    distancias[distancias == sin_conexion] = np.inf
    np.fill_diagonal(distancias, 0)

    recorridos = np.full((n, n), -1, dtype=int)
    for i in range(n):
        for j in range(n):
            if i != j and np.isfinite(distancias[i][j]):
                recorridos[i][j] = j

    for k in range(n):
        for i in range(n):
            for j in range(n):
                nueva_distancia = distancias[i][k] + distancias[k][j]
                if nueva_distancia < distancias[i][j]:
                    distancias[i][j] = nueva_distancia
                    recorridos[i][j] = recorridos[i][k]

    return distancias, recorridos


def obtener_ruta_minima(recorridos, lista_municipios, origen_idx, destino_idx):
    """
    Reconstruye la lista exacta de municipios usando la matriz de recorridos.
    """
    if origen_idx == destino_idx:
        return [lista_municipios[origen_idx]]

    if recorridos[origen_idx][destino_idx] == -1:
        return []

    ruta = [lista_municipios[origen_idx]]
    actual_idx = origen_idx

    while actual_idx != destino_idx:
        actual_idx = recorridos[actual_idx][destino_idx]

        if actual_idx == -1:
            return []

        ruta.append(lista_municipios[actual_idx])

    return ruta


def _obtener_indice(lista_municipios, municipio):
    """
    Permite buscar un municipio por nombre o usar directamente su indice.
    """
    if isinstance(municipio, int):
        if municipio < 0 or municipio >= len(lista_municipios):
            raise ValueError("El indice del municipio esta fuera de rango.")
        return municipio

    try:
        return lista_municipios.index(municipio)
    except ValueError as exc:
        raise ValueError(f"El municipio '{municipio}' no existe en la lista.") from exc


def calcular_ruta_floyd(matriz_distancias, lista_municipios, origen, destino):
    """
    Funcion principal del integrante 2.

    Recibe la matriz de distancias, la lista de municipios, un origen y un
    destino. Devuelve dos datos claros:
    1. total_km: kilometros de la ruta mas corta.
    2. ruta: lista exacta de municipios por los que se debe pasar.
    """
    origen_idx = _obtener_indice(lista_municipios, origen)
    destino_idx = _obtener_indice(lista_municipios, destino)

    distancias, recorridos = aplicar_floyd_warshall(matriz_distancias)
    total_km = distancias[origen_idx][destino_idx]
    ruta = obtener_ruta_minima(
        recorridos,
        lista_municipios,
        origen_idx,
        destino_idx,
    )

    if not np.isfinite(total_km):
        return float("inf"), []

    if float(total_km).is_integer():
        total_km = int(total_km)
    else:
        total_km = float(total_km)

    return total_km, ruta


if __name__ == "__main__":
    import lector_excel

    print("Iniciando prueba de Floyd-Warshall...\n")

    municipios, matriz = lector_excel.cargar_datos()

    if len(municipios) > 0:
        origen_prueba = "GUATEMALA"
        destino_prueba = "LA ANTIGUA GUATEMALA"

        print("Lista de municipios leida:", municipios)

        try:
            kilometros, ruta = calcular_ruta_floyd(
                matriz,
                municipios,
                origen_prueba,
                destino_prueba,
            )

            print("-" * 40)
            print(f"Origen: {origen_prueba}")
            print(f"Destino: {destino_prueba}")

            if ruta:
                print(f"Distancia mas corta: {kilometros} km")
                print(f"Ruta a seguir: {ruta}")
            else:
                print("No existe una ruta disponible entre esos municipios.")

            print("-" * 40)
        except ValueError as error:
            print(f"Error: {error}")

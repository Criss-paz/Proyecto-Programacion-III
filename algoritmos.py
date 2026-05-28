import numpy as np

def aplicar_floyd_warshall(matriz_distancias):
    """
    Ejecuta el algoritmo de Floyd-Warshall.
    Recibe la matriz original y devuelve dos matrices:
    1. distancias: Contiene el costo mínimo entre todos los pares.
    2. recorrido: Contiene los nodos intermedios para reconstruir la ruta.
    """
    n = len(matriz_distancias)
    
    # 1. Hacemos una copia de la matriz original para no alterarla
    distancias = np.copy(matriz_distancias)
    
    # 2. Creamos una matriz de "recorridos" llena de -1
    recorrido = np.full((n, n), -1)
    
    # 3. Inicializamos la matriz de recorridos
    # Si hay una ruta directa (que no sea a sí mismo y no sea 999)
    for i in range(n):
        for j in range(n):
            if i != j and distancias[i][j] != 999:
                recorrido[i][j] = j
                
    # 4. El corazón de Floyd-Warshall (los 3 ciclos anidados)
    # Compara si ir de 'i' a 'j' pasando por 'k' es más corto que ir directo.
    for k in range(n):
        for i in range(n):
            for j in range(n):
                # Si la ruta pasando por k es más corta, actualizamos
                if distancias[i][k] + distancias[k][j] < distancias[i][j]:
                    distancias[i][j] = distancias[i][k] + distancias[k][j]
                    # Guardamos por dónde tuvimos que pasar
                    recorrido[i][j] = recorrido[i][k]
                    
    return distancias, recorrido

def obtener_ruta_minima(recorrido, lista_municipios, origen_idx, destino_idx):
    """
    Reconstruye la lista de municipios (la ruta) usando la matriz de recorridos.
    """
    # Si el valor sigue siendo -1, significa que no hay camino posible
    if recorrido[origen_idx][destino_idx] == -1:
        return []
        
    ruta = [lista_municipios[origen_idx]]
    actual_idx = origen_idx
    
    while actual_idx != destino_idx:
        actual_idx = recorrido[actual_idx][destino_idx]
        ruta.append(lista_municipios[actual_idx])
        
    return ruta


# --- ZONA DE PRUEBAS ---
if __name__ == '__main__':
    print("Iniciando prueba de Floyd-Warshall...\n")
    
    import lector_excel
    
    # 1. Cargamos los datos reales del Excel
    municipios, matriz = lector_excel.cargar_datos()
    
    if len(municipios) > 0:
        # 2. Elegimos dos municipios de prueba (ej. posiciones 0 y 14)
        origen_prueba = "GUATEMALA"
        destino_prueba = "LA ANTIGUA GUATEMALA"
        print("Lista de municipios leída:", municipios)
        if origen_prueba not in municipios or destino_prueba not in municipios:
            print("Error: el origen o destino no existe en el Excel.")
            print(f"Origen buscado: {origen_prueba}")
            print(f"Destino buscado: {destino_prueba}")
            print("Usa exactamente uno de los nombres mostrados en la lista.")
            exit()

        idx_origen = municipios.index(origen_prueba)
        idx_destino = municipios.index(destino_prueba)
        
        # 3. Aplicamos Floyd-Warshall
        print("Calculando todas las rutas posibles (Floyd-Warshall)...")
        matriz_minima, matriz_recorrido = aplicar_floyd_warshall(matriz)
        
        # 4. Extraemos la distancia y la ruta exacta
        distancia_km = matriz_minima[idx_origen][idx_destino]
        nodos_ruta = obtener_ruta_minima(matriz_recorrido, municipios, idx_origen, idx_destino)
        
        # 5. Mostramos los resultados
        print("-" * 40)
        print(f"Origen: {origen_prueba}")
        print(f"Destino: {destino_prueba}")
        print(f"Distancia más corta: {distancia_km} km")
        print(f"Ruta a seguir: {nodos_ruta}")
        print("-" * 40)

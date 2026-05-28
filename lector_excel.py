import pandas as pd
import numpy as np

def cargar_datos():
    """
    Lee el archivo de Excel y devuelve una lista con los nombres
    de los municipios y una matriz de Numpy con las distancias.
    """
    try:
        # 1. Leer el archivo Excel
        # index_col=0 le dice a Pandas que la primera columna vertical 
        # contiene los nombres y no es parte de las distancias matemáticas.
        df = pd.read_excel('distancias.xlsx', index_col=0)

        # 2. Extraer la lista de municipios
        # Tomamos los nombres de las filas (index) y los convertimos en una lista normal
        lista_municipios = df.index.tolist()

        # 3. Crear la matriz de distancias
        # .to_numpy() agarra exclusivamente los números de la tabla y descarta el texto
        matriz_distancias = df.to_numpy()

        return lista_municipios, matriz_distancias

    except FileNotFoundError:
        print("Error: No se encontró el archivo 'distancias.xlsx'.")
        print("Asegúrate de que esté en la misma carpeta que este script.")
        return [], np.array([])
    except Exception as e:
        print(f"Ocurrió un error inesperado al leer el Excel: {e}")
        return [], np.array([])

# --- ZONA DE PRUEBAS ---
# Este bloque de código SOLO se ejecuta si corres este archivo directamente.
# Si el archivo api_servidor.py importa este código, esto no se ejecutará.
if __name__ == '__main__':
    print("Iniciando prueba de lectura de Excel...")
    
    municipios, matriz = cargar_datos()
    
    if len(municipios) > 0:
        print("\n¡Lectura Exitosa!")
        print(f"Total de municipios cargados: {len(municipios)}")
        print(f"Primeros 5 municipios: {municipios[:5]}")
        print(f"Dimensiones de la matriz de Numpy: {matriz.shape}")
        
        # Muestra un pedacito de la matriz para confirmar que son números
        print("\nMuestra de la matriz (primeros 3x3):")
        print(matriz[:3, :3])
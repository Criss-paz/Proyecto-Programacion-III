"""Lee la matriz de distancias de Excel."""

from pathlib import Path
import pandas as pd
import numpy as np

# Ahora busca el archivo en la MISMA carpeta donde está este script
RUTA_EXCEL = Path(__file__).resolve().parent / "distancias.xlsx"

def cargar_datos(ruta_excel=RUTA_EXCEL):
    """Devuelve (lista_municipios, matriz_numpy)."""
    try:
        # Extrae los datos limpiando los espacios invisibles en los nombres
        df = pd.read_excel(ruta_excel, index_col=0)
        lista_limpia = [str(nombre).strip() for nombre in df.index.tolist()]
        return lista_limpia, df.to_numpy()
    except Exception as e:
        print(f"Error al leer Excel: {e}")
        return [], np.array([])

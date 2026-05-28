"""Lee la matriz de distancias desde datos/distancias.xlsx."""

from pathlib import Path
import pandas as pd
import numpy as np

# Ruta fija respecto a la carpeta datos/ del proyecto
RUTA_EXCEL = Path(__file__).resolve().parent.parent / "datos" / "distancias.xlsx"


def cargar_datos(ruta_excel=RUTA_EXCEL):
    """Devuelve (lista_municipios, matriz_numpy)."""
    try:
        df = pd.read_excel(ruta_excel, index_col=0)
        return df.index.tolist(), df.to_numpy()
    except Exception as e:
        print(f"Error al leer Excel: {e}")
        return [], np.array([])

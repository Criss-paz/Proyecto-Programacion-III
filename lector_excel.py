import pandas as pd
from pathlib import Path

def cargar_datos():
    """Lee el Excel y devuelve (lista_municipios, matriz_numpy)."""
    try:
        ruta = Path(__file__).resolve().parent / "distancias.xlsx"
        df = pd.read_excel(ruta, index_col=0)
        return [str(m).strip() for m in df.index], df.to_numpy()
    except Exception as e:
        print(f"Error leyendo Excel: {e}")
        return [], []
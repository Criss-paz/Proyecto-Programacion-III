"""Tarifas usadas por el cotizador.

Los valores se guardan aqui para que el panel Administrador pueda editarlos.
"""

import re
from pathlib import Path

# === INICIO TARIFAS ===
TARIFAS = {
    "COSTO_BASE": 15.0,
    "COSTO_POR_KM": 2.5,
    "COSTO_POR_LIBRA": 0.5,
    "MARGEN_UTILIDAD": 0.4,
}
# === FIN TARIFAS ===

RUTA_ARCHIVO = Path(__file__)


def obtener():
    """Devuelve una copia para evitar cambios accidentales."""
    return TARIFAS.copy()


def guardar(valores):
    """Actualiza las tarifas en memoria y las escribe en este archivo."""
    for clave in TARIFAS:
        if clave in valores:
            TARIFAS[clave] = float(valores[clave])
    return _guardar_en_archivo()


def calcular_factura(km, peso):
    """Aplica la formula solicitada por el proyecto."""
    costo_base = TARIFAS["COSTO_BASE"]
    costo_km = TARIFAS["COSTO_POR_KM"]
    costo_libra = TARIFAS["COSTO_POR_LIBRA"]
    margen = TARIFAS["MARGEN_UTILIDAD"]

    costo_total = costo_base + (costo_km * km) + (costo_libra * peso)
    precio_final = costo_total * (1 + margen)
    return costo_base, costo_km, costo_libra, costo_total, precio_final


def _guardar_en_archivo():
    try:
        texto = RUTA_ARCHIVO.read_text(encoding="utf-8")
        RUTA_ARCHIVO.write_text(_reemplazar_bloque_tarifas(texto), encoding="utf-8")
        return True
    except Exception:
        return False


def _reemplazar_bloque_tarifas(texto):
    bloque = "TARIFAS = {\n"
    bloque += "".join(f'    "{clave}": {valor},\n' for clave, valor in TARIFAS.items())
    bloque += "}"

    patron = r"# === INICIO TARIFAS ===\nTARIFAS = \{.*?\}\n# === FIN TARIFAS ==="
    return re.sub(
        patron,
        f"# === INICIO TARIFAS ===\n{bloque}\n# === FIN TARIFAS ===",
        texto,
        count=1,
        flags=re.DOTALL,
    )

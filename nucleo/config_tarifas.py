"""
Archivo ÚNICO de tarifas del proyecto.
Edita TARIFAS aquí o usa el panel Administrador del cliente.
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

_RUTA = Path(__file__)


def obtener():
    return TARIFAS.copy()


def guardar(valores):
    for clave in TARIFAS:
        if clave in valores:
            TARIFAS[clave] = float(valores[clave])
    return _persistir()


def _persistir():
    try:
        texto = _RUTA.read_text(encoding="utf-8")
        bloque = "TARIFAS = {\n" + "".join(f'    "{k}": {TARIFAS[k]},\n' for k in TARIFAS) + "}"
        nuevo = re.sub(
            r"# === INICIO TARIFAS ===\nTARIFAS = \{.*?\}\n# === FIN TARIFAS ===",
            f"# === INICIO TARIFAS ===\n{bloque}\n# === FIN TARIFAS ===",
            texto, count=1, flags=re.DOTALL,
        )
        _RUTA.write_text(nuevo, encoding="utf-8")
        return True
    except Exception:
        return False


def calcular_factura(km, peso):
    t = TARIFAS
    costo_total = t["COSTO_BASE"] + (t["COSTO_POR_KM"] * km) + (t["COSTO_POR_LIBRA"] * peso)
    precio_final = costo_total * (1 + t["MARGEN_UTILIDAD"])
    return t["COSTO_BASE"], t["COSTO_POR_KM"], t["COSTO_POR_LIBRA"], costo_total, precio_final

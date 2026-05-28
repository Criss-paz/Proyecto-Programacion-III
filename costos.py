"""
Formulas de cobro para el Integrante 3.

Los valores no son aleatorios:
- Costo base: gastos fijos de operacion por cada paquete.
- Costo por km: combustible, mantenimiento y depreciacion del vehiculo.
- Costo por libra: manipulacion y esfuerzo de carga del paquete.
- Utilidad: ganancia del 30% para la empresa.
"""

COSTO_BASE = 15.00
COSTO_KM = 3.50
COSTO_LIBRA = 1.25
UTILIDAD = 0.30


def calcular_factura(kilometros, peso_libras):
    """
    Recibe los kilometros de la ruta y el peso del paquete.
    Aplica las formulas del proyecto y devuelve todos los valores.
    """
    costo_total = COSTO_BASE + (COSTO_KM * kilometros) + (COSTO_LIBRA * peso_libras)
    precio_final = costo_total + (costo_total * UTILIDAD)

    return COSTO_BASE, COSTO_KM, COSTO_LIBRA, costo_total, precio_final


def obtener_detalle_costos():
    """Devuelve los parametros para mostrarlos o explicarlos en pantalla."""
    return {
        "costo_base": COSTO_BASE,
        "costo_km": COSTO_KM,
        "costo_libra": COSTO_LIBRA,
        "utilidad": UTILIDAD,
    }

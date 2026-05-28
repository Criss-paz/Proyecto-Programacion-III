def calcular_factura(kilometros, peso_libras):
    """
    Recibe los kilómetros de la ruta y el peso del paquete.
    Aplica las fórmulas del proyecto y devuelve todos los valores.
    """
    # 1. Definición de precios de la empresa (Pueden cambiar estos valores si gustan)
    costo_base = 15.00      # Gastos fijos (papelería, luz, etc.)
    costo_km = 3.50         # Q3.50 por km (Cubre gasolina y depreciación del vehículo)
    costo_libra = 1.25      # Q1.25 por cada libra de peso
    utilidad = 0.30         # 30% de ganancia para la empresa (0.30)

    # 2. Fórmulas exactas solicitadas en el PDF
    costo_total = costo_base + (costo_km * kilometros) + (costo_libra * peso_libras)
    precio_final = costo_total + (costo_total * utilidad)

    return costo_base, costo_km, costo_libra, costo_total, precio_final
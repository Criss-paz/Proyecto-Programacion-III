# Procedimiento para definir costos y utilidad

Empresa: Envios Rapidos GT

Este documento explica de forma clara como se definieron los valores usados por el cotizador. Los montos no son aleatorios: se basan en costos operativos estimados para un envio terrestre entre municipios.

## Formula usada

```text
Costo_total = Costo_base + (Costo_km * kilometros) + (Costo_libra * peso_paquete)
Precio_final = Costo_total + Costo_total * Utilidad
```

En el programa, la segunda formula se aplica de forma equivalente:

```text
Precio_final = Costo_total * (1 + Utilidad)
```

## Valores configurados

Los valores actuales estan en `nucleo/config_tarifas.py`.

| Concepto | Valor | Justificacion |
|---|---:|---|
| Costo_base | Q15.00 | Cubre gastos fijos de operacion: papeleria, energia electrica, uso de sistema, atencion en agencia y preparacion del paquete. |
| Costo_km | Q2.50/km | Estima combustible, salario proporcional del piloto, mantenimiento, llantas, depreciacion del vehiculo y gastos de ruta. |
| Costo_libra | Q0.50/lb | Cubre el esfuerzo adicional por manipular paquetes mas pesados y el impacto del peso en consumo y desgaste. |
| Utilidad | 40% | Margen de ganancia elegido por la empresa para cubrir riesgo operativo y obtener beneficio comercial. |

## Calculo del costo por kilometro

Se asumio un vehiculo de reparto liviano que recorre rutas asfaltadas entre agencias municipales.

| Factor | Estimacion por km |
|---|---:|
| Combustible | Q1.10 |
| Mantenimiento y llantas | Q0.45 |
| Depreciacion del vehiculo | Q0.40 |
| Salario proporcional del piloto | Q0.40 |
| Gastos menores de ruta | Q0.15 |
| Total estimado | Q2.50 |

Por eso se usa:

```text
Costo_km = Q2.50
```

## Calculo del costo por libra

El costo por libra se definio considerando manipulacion del paquete, espacio ocupado y aumento de esfuerzo/carga durante el transporte.

```text
Costo_libra = Q0.50
```

## Ejemplo

Si una ruta mide 43 km y el paquete pesa 5 lb:

```text
Costo_total = 15 + (2.50 * 43) + (0.50 * 5)
Costo_total = Q125.00

Precio_final = 125 + (125 * 0.40)
Precio_final = Q175.00
```

El cliente paga Q175.00.

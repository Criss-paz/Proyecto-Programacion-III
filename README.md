# Envios Rapidos GT - Sistema de Rutas y Cotizaciones

Aplicacion cliente-servidor en Python para cotizar envios entre municipios de Guatemala usando Floyd-Warshall, Flask, Tkinter, Matplotlib y NetworkX.

Departamentos elegidos: Guatemala, Sacatepequez y Chimaltenango. El algoritmo de Dijkstra se omite por indicacion del catedratico; el calculo de rutas minimas se realiza con Floyd-Warshall.

Para exponer el proyecto, revisar:

- `docs/GUIA_EXPOSICION.md`: guia de funcionamiento por archivo.
- `docs/TARIFAS.md`: procedimiento usado para definir costo base, costo por kilometro, costo por libra y utilidad.

## Estructura

```text
api.py                 -> inicia el servidor Flask
principal.py           -> inicia el cliente Tkinter
datos/distancias.xlsx  -> matriz de distancias entre municipios
datos/grafo.drawio     -> grafo elaborado en draw.io
nucleo/                -> lectura de Excel, Floyd-Warshall y tarifas
servidor/              -> API REST
cliente/               -> interfaz grafica
docs/                  -> documentacion de exposicion y tarifas
```

## Ejecucion

Instalar dependencias:

```bash
pip install -r requirements.txt
```

Opcion recomendada:

```bash
python principal.py
```

El cliente intenta iniciar la API automaticamente.

Tambien se puede ejecutar por separado:

```bash
python api.py
python principal.py
```

## API

| Metodo | Ruta | Descripcion |
|---|---|---|
| GET | `/status` | Estado del servidor y dimensiones de la matriz |
| GET | `/datos` | Municipios y matriz original |
| GET | `/ruta?origen=X&destino=Y` | Kilometros y ruta mas corta |
| GET | `/floyd` | Matriz resultante de Floyd-Warshall y matriz de recorridos |

## Tarifas

Valores actuales:

```text
Costo_base = Q15.00
Costo_km = Q2.50/km
Costo_libra = Q0.50/lb
Utilidad = 40%
```

Formula:

```text
Costo_total = Costo_base + (Costo_km * kilometros) + (Costo_libra * peso_paquete)
Precio_final = Costo_total + Costo_total * Utilidad
```

La justificacion completa esta en `docs/TARIFAS.md`.

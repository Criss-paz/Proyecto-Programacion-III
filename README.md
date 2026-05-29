# Envios Rapidos GT - Sistema de Rutas y Cotizaciones

Aplicacion cliente-servidor en Python para cotizar envios entre municipios de Guatemala usando Floyd-Warshall, Flask, Tkinter, Matplotlib y NetworkX.

Departamentos elegidos: Guatemala, Sacatepequez y Chimaltenango. El algoritmo de Dijkstra se omite por indicacion del catedratico; el calculo de rutas minimas se realiza con Floyd-Warshall.

Para exponer el proyecto, revisar:

- `docs/GUIA_EXPOSICION.md`: guia de funcionamiento por archivo.
- `docs/TARIFAS.md`: procedimiento usado para definir costo base, costo por kilometro, costo por libra y utilidad.

## Estructura

```text
api_servidor.py       -> inicia el servidor Flask/API
cliente_ui.py         -> inicia el cliente grafico Tkinter
distancias.xlsx       -> matriz de distancias entre municipios
grafo.drawio          -> grafo elaborado en draw.io
lector_excel.py       -> lectura del archivo Excel
algoritmos.py         -> algoritmo Floyd-Warshall y reconstruccion de ruta
config_tarifas.py     -> costos base, por km, por libra y utilidad
visualizador_grafo.py -> dibujo del grafo con NetworkX y Matplotlib
logo.png              -> logo de la empresa
docs/                 -> documentacion de exposicion y tarifas
```

## Ejecucion

Instalar dependencias:

```bash
pip install -r requirements.txt
```

Ejecutar el servidor en una terminal:

```bash
python api_servidor.py
```

Ejecutar el cliente en otra terminal:

```bash
python cliente_ui.py
```

El servidor debe quedar activo en `http://127.0.0.1:5000` mientras se usa el cliente.

## API

| Metodo | Ruta | Descripcion |
|---|---|---|
| POST | `/calcular_ruta` | Recibe `origen` y `destino`; devuelve kilometros y nodos de la ruta mas corta calculada con Floyd-Warshall. |

Ejemplo de cuerpo JSON:

```json
{
  "origen": "GUATEMALA",
  "destino": "LA ANTIGUA GUATEMALA"
}
```

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

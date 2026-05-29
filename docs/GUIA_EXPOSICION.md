# Guia de exposicion - Envios Rapidos GT

## Idea general

El sistema simula una empresa de transporte que tiene agencias en cabeceras municipales. El empleado selecciona origen, destino y peso del paquete. La API calcula la ruta mas corta con Floyd-Warshall y el cliente muestra kilometros, ruta, costos y precio final.

Departamentos elegidos: Guatemala, Sacatepequez y Chimaltenango. Dijkstra se omite por indicacion del catedratico, por lo que la explicacion del algoritmo se centra en Floyd-Warshall.

## Capas del proyecto

```text
datos/distancias.xlsx
        -> nucleo/lector_excel.py
        -> servidor/app.py
        -> nucleo/algoritmos.py
        -> cliente/vista_cotizador.py
```

## Archivos importantes

| Archivo | Funcion |
|---|---|
| `principal.py` | Inicia la aplicacion de escritorio y levanta la API si hace falta. |
| `api.py` | Inicia el servidor Flask. |
| `datos/distancias.xlsx` | Matriz de distancias en kilometros. |
| `datos/grafo.drawio` | Grafo elaborado en draw.io. |
| `nucleo/lector_excel.py` | Lee el Excel y devuelve municipios + matriz NumPy. |
| `nucleo/algoritmos.py` | Ejecuta Floyd-Warshall y reconstruye la ruta minima. |
| `nucleo/config_tarifas.py` | Guarda costo base, costo por km, costo por libra y utilidad. |
| `servidor/app.py` | Expone `/datos`, `/ruta`, `/floyd` y `/status`. |
| `cliente/aplicacion.py` | Ventana principal, nombre de empresa, logo y estado de API. |
| `cliente/vista_cotizador.py` | Formulario de origen, destino, peso, ruta y factura. |
| `cliente/vista_admin.py` | Estado de datos, tarifas y matriz resultante de Floyd. |
| `cliente/visualizador_grafo.py` | Dibuja el grafo no dirigido con NetworkX y Matplotlib. |

## Algoritmo Floyd-Warshall

El algoritmo esta en `nucleo/algoritmos.py`.

1. Recibe una matriz cuadrada de distancias.
2. Convierte valores sin conexion a infinito.
3. Recorre todos los vertices intermedios `k`.
4. Para cada origen `i` y destino `j`, compara si pasar por `k` reduce la distancia.
5. Guarda dos matrices:
   - matriz de distancias minimas;
   - matriz de recorridos para reconstruir la ruta.

La API expone la matriz resultante en:

```text
GET /floyd
```

En la aplicacion se puede ver desde:

```text
Administrador -> Ver Matriz Floyd
```

## Grafo no dirigido

El visualizador usa `nx.Graph()` porque el catedratico indico que el grafo debe manejarse como no dirigido.

La matriz del Excel es simetrica, por lo que la distancia de ida y vuelta entre dos municipios es la misma. Por esa razon, en pantalla se dibuja una sola arista entre cada par de municipios y no se muestran flechas.

## Formula de cobro

```text
Costo_total = Costo_base + (Costo_km * kilometros) + (Costo_libra * peso_paquete)
Precio_final = Costo_total + Costo_total * Utilidad
```

Los valores y su justificacion estan documentados en `docs/TARIFAS.md`.

## Demostracion sugerida

1. Ejecutar `python principal.py`.
2. Confirmar que la API aparece como conectada.
3. Seleccionar origen `GUATEMALA`.
4. Seleccionar destino `LA ANTIGUA GUATEMALA`.
5. Ingresar peso `5`.
6. Presionar `Calcular`.
7. Mostrar:
   - ruta resaltada en el grafo;
   - kilometros en azul;
   - costo total;
   - precio final en rojo.
8. Ir a `Administrador`.
9. Mostrar lista de municipios, tarifas y matriz Floyd.

## Ejemplo de resultado

Para `GUATEMALA -> LA ANTIGUA GUATEMALA` con 5 lb:

```text
Ruta: GUATEMALA -> MIXCO -> SAN LUCAS SACATEPEQUEZ -> SANTA LUCIA MILPAS ALTAS -> LA ANTIGUA GUATEMALA
Distancia: 43 km
Costo total: Q125.00
Precio final: Q175.00
```

## Preguntas probables

**Donde se cargan los datos?**  
En `nucleo/lector_excel.py`, desde `datos/distancias.xlsx`.

**Donde esta Floyd?**  
En `nucleo/algoritmos.py`, funcion `aplicar_floyd_warshall`.

**Como se reconstruye la ruta?**  
Con la matriz de recorridos, siguiendo el siguiente nodo desde el origen hasta llegar al destino.

**Por que hay API?**  
Para separar el calculo de rutas de la interfaz grafica y cumplir los puntos extra cliente-servidor.

**Donde estan las tarifas?**  
En `nucleo/config_tarifas.py`; la justificacion esta en `docs/TARIFAS.md`.

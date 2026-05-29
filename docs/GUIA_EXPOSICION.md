# Guia de exposicion - Envios Rapidos GT

## Idea general

El sistema simula una empresa de transporte que tiene agencias en cabeceras municipales. El empleado selecciona origen, destino y peso del paquete. La API calcula la ruta mas corta con Floyd-Warshall y el cliente muestra kilometros, ruta, costos y precio final.

Departamentos elegidos: Guatemala, Sacatepequez y Chimaltenango. Dijkstra se omite por indicacion del catedratico, por lo que la explicacion del algoritmo se centra en Floyd-Warshall.

## Flujo del sistema

```text
distancias.xlsx
        -> lector_excel.py
        -> api_servidor.py
        -> algoritmos.py
        -> cliente_ui.py
        -> visualizador_grafo.py
```

## Archivos importantes

| Archivo | Funcion |
|---|---|
| `api_servidor.py` | Inicia el servidor Flask y expone la ruta `/calcular_ruta`. |
| `cliente_ui.py` | Interfaz grafica Tkinter para seleccionar origen, destino, peso y mostrar la cotizacion. |
| `distancias.xlsx` | Matriz de distancias en kilometros entre municipios. |
| `grafo.drawio` | Grafo elaborado en draw.io y aprobado para la entrega. |
| `lector_excel.py` | Lee el Excel y devuelve municipios + matriz NumPy. |
| `algoritmos.py` | Ejecuta Floyd-Warshall y reconstruye la ruta minima. |
| `config_tarifas.py` | Guarda costo base, costo por km, costo por libra y utilidad. |
| `visualizador_grafo.py` | Dibuja el grafo con NetworkX y Matplotlib usando posiciones del archivo Draw.io. |
| `logo.png` | Logo usado para personalizar la empresa. |

## Algoritmo Floyd-Warshall

El algoritmo esta en `algoritmos.py`, funcion `aplicar_floyd_warshall`.

1. Recibe una matriz cuadrada de distancias.
2. Convierte valores sin conexion a infinito.
3. Recorre todos los vertices intermedios `k`.
4. Para cada origen `i` y destino `j`, compara si pasar por `k` reduce la distancia.
5. Guarda dos matrices:
   - matriz de distancias minimas;
   - matriz de recorridos para reconstruir la ruta.

La ruta se reconstruye con `obtener_ruta_minima`, siguiendo la matriz de recorridos desde el origen hasta llegar al destino.

## API cliente-servidor

La aplicacion esta dividida en dos partes para cumplir los puntos extra:

```text
Servidor/API: api_servidor.py
Cliente GUI:  cliente_ui.py
```

El cliente envia origen y destino a:

```text
POST /calcular_ruta
```

La API responde con:

```text
distancia_km
ruta_optima
mensaje
```

El peso no se envia a la API porque el cliente lo usa localmente para calcular el costo del envio despues de recibir los kilometros.

## Grafo

El grafo fue elaborado en `grafo.drawio`. Para mostrarlo en pantalla, `visualizador_grafo.py` crea un grafo con `nx.Graph()` y usa Matplotlib para dibujarlo.

El visualizador lee las posiciones del archivo Draw.io para que el mapa se parezca al grafo aprobado. La ruta mas corta se resalta en rojo y los demas nodos/aristas quedan en colores suaves.

## Formula de cobro

```text
Costo_total = Costo_base + (Costo_km * kilometros) + (Costo_libra * peso_paquete)
Precio_final = Costo_total + Costo_total * Utilidad
```

Los valores y su justificacion estan documentados en `docs/TARIFAS.md`.

## Demostracion sugerida

1. Ejecutar el servidor:

```text
python api_servidor.py
```

2. Ejecutar el cliente:

```text
python cliente_ui.py
```

3. Seleccionar origen `GUATEMALA`.
4. Seleccionar destino `LA ANTIGUA GUATEMALA`.
5. Ingresar peso `5`.
6. Presionar `Calcular Ruta y Ver Mapa`.
7. Mostrar:
   - ruta resaltada en el grafo;
   - kilometros en azul;
   - costo total;
   - precio final en rojo.

## Ejemplo de resultado

Para `GUATEMALA -> LA ANTIGUA GUATEMALA` con 5 lb, el sistema muestra la ruta minima calculada por Floyd-Warshall, la distancia en kilometros y la cotizacion con las tarifas configuradas.

## Preguntas probables

**Donde se cargan los datos?**  
En `lector_excel.py`, desde `distancias.xlsx`.

**Donde esta Floyd-Warshall?**  
En `algoritmos.py`, funcion `aplicar_floyd_warshall`.

**Como se reconstruye la ruta?**  
Con la matriz de recorridos, siguiendo el siguiente nodo desde el origen hasta llegar al destino.

**Por que hay API?**  
Para separar el calculo de rutas de la interfaz grafica y cumplir los puntos extra cliente-servidor.

**Donde estan las tarifas?**  
En `config_tarifas.py`; la justificacion esta en `docs/TARIFAS.md`.

**Que datos devuelve la API?**  
Devuelve los kilometros de la ruta mas corta y los nodos por los que se pasa.

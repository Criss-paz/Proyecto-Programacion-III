# Guía de exposición — Envíos Rápidos GT

Documento para presentar el proyecto al ingeniero del curso **archivo por archivo**, en el orden recomendado.

---

## 1. Estructura del proyecto

```
Proyecto-Programacion-III/
├── api.py                 ← INICIO servidor (Capa 3)
├── principal.py           ← INICIO cliente (Capa 4)
├── requirements.txt
├── datos/                 ← Capa 1: archivos de entrada
│   ├── distancias.xlsx
│   └── grafo.drawio
├── nucleo/                ← Capa 2: lógica de negocio
│   ├── lector_excel.py
│   ├── algoritmos.py
│   └── config_tarifas.py
├── servidor/              ← Capa 3: API Flask
│   └── app.py
└── cliente/               ← Capa 4: interfaz Tkinter
    ├── aplicacion.py
    ├── ui_helpers.py
    ├── vista_cotizador.py
    ├── vista_admin.py
    └── visualizador_grafo.py
```

### Flujo general

```
[datos/distancias.xlsx]
        ↓
[nucleo/lector_excel] → matriz + municipios
        ↓
[servidor/app.py]  ←—— HTTP JSON ——→  [cliente/aplicacion.py]
        ↓                                      ↓
[nucleo/algoritmos]                    [nucleo/config_tarifas]
   Floyd-Warshall                         cotización Q
        ↓                                      ↓
   km + ruta                            precio final
```

---

## 2. Orden de lectura para la exposición

| Paso | Archivo | Qué decir en una frase |
|------|---------|------------------------|
| 1 | `principal.py` | Arranca el cliente y carga las tarifas. |
| 2 | `api.py` | Arranca el servidor Flask. |
| 3 | `datos/distancias.xlsx` | Matriz 49×49 de distancias en km entre municipios. |
| 4 | `nucleo/lector_excel.py` | Lee el Excel y devuelve listas para Python. |
| 5 | `nucleo/algoritmos.py` | Floyd-Warshall: ruta más corta. |
| 6 | `nucleo/config_tarifas.py` | **Único archivo** de precios y fórmulas. |
| 7 | `servidor/app.py` | API REST: `/datos`, `/ruta`, `/status`. |
| 8 | `cliente/aplicacion.py` | Ventana principal y conexión a la API. |
| 9 | `cliente/vista_cotizador.py` | Formulario, cotización y mapa. |
| 10 | `cliente/vista_admin.py` | Lista municipios y edición de tarifas. |
| 11 | `cliente/ui_helpers.py` | Colores y widgets reutilizables. |
| 12 | `cliente/visualizador_grafo.py` | Grafo con matplotlib + posiciones draw.io. |

---

## 3. Explicación por archivo (línea por línea resumida)

### `principal.py` (cliente)

| Líneas | Qué hace |
|--------|----------|
| 1-4 | Docstring: indica que es el punto de entrada del cliente. |
| 6-7 | Importa Tkinter, tarifas y la clase de la ventana. |
| 9-14 | Si ejecutas este archivo directamente: carga tarifas, crea ventana, inicia la app. |

### `api.py` (servidor)

| Líneas | Qué hace |
|--------|----------|
| 1-4 | Docstring del servidor. |
| 6-9 | Importa `iniciar()` de `servidor/app.py` y lo ejecuta. |

### `nucleo/lector_excel.py`

| Líneas | Qué hace |
|--------|----------|
| 1-2 | Documentación del módulo. |
| 4-8 | Importa librerías y define ruta a `datos/distancias.xlsx`. |
| 11-18 | `cargar_datos()`: lee Excel con pandas, devuelve nombres y matriz NumPy. |

### `nucleo/algoritmos.py`

| Líneas | Qué hace |
|--------|----------|
| 5 | `SIN_CONEXION = 999`: valor del Excel cuando no hay camino. |
| 8-28 | `aplicar_floyd_warshall`: triple bucle k,i,j para distancias mínimas. |
| 15-19 | Inicializa matriz `recorridos` para reconstruir la ruta. |
| 31-42 | `obtener_ruta_minima`: sigue punteros desde origen a destino. |
| 45-51 | `_indice`: convierte nombre de municipio a número de fila. |
| 54-61 | `calcular_ruta_floyd`: función que usa la API — devuelve km y lista. |

### `nucleo/config_tarifas.py`

| Líneas | Qué hace |
|--------|----------|
| 9-16 | Bloque `TARIFAS`: **edita aquí** base, km, libra y margen. |
| 21-23 | `obtener()`: devuelve copia de tarifas actuales. |
| 26-31 | `guardar()`: actualiza valores (desde Administrador). |
| 34-48 | `_persistir()`: escribe cambios en este mismo archivo. |
| 51-55 | `calcular_factura(km, peso)`: aplica fórmulas del README. |

**Fórmulas:**
- Costo = Base + (Q/km × km) + (Q/lb × peso)
- Precio final = Costo × (1 + margen)

### `servidor/app.py`

| Líneas | Qué hace |
|--------|----------|
| 8-12 | Crea app Flask y carga datos al iniciar (una sola vez). |
| 15-17 | `_matriz_json`: convierte infinito/NaN a 999 para JSON. |
| 20-29 | `_respuesta_ruta`: valida parámetros y llama a Floyd. |
| 32-34 | `GET /datos`: municipios + matriz para el cliente. |
| 37-40 | `GET /status`: diagnóstico (49 municipios, 49×49). |
| 43-46 | `GET /ruta?origen=&destino=`: km y ruta óptima. |
| 49-51 | Error 404 para rutas inexistentes. |
| 54-56 | `iniciar()`: levanta servidor en puerto 5000. |

### `cliente/aplicacion.py`

| Líneas | Qué hace |
|--------|----------|
| 19 | Hereda Cotizador + Admin + helpers de UI. |
| 21-33 | Configura ventana, variables de estado, estilos ttk. |
| 35-38 | Crea encabezado y área de contenido; llama a API. |
| 40-54 | Barra superior: título, estado API, botones Cotizador/Admin. |
| 56-66 | `cambiar_pestana` / `refrescar_vista`: cambia pantalla. |
| 68-69 | `_api`: petición HTTP con `requests`. |
| 71-84 | `reconectar_api`: GET `/datos`, guarda matriz o muestra error. |
| 86-91 | Pantalla de error si la API no está encendida. |

### `cliente/vista_cotizador.py`

| Líneas | Qué hace |
|--------|----------|
| 10-26 | `mostrar_cotizador`: layout dos columnas (formulario + mapa). |
| 28-47 | Formulario: combos origen/destino, peso, botones, resultados. |
| 49-74 | Controles de zoom y panel del mapa. |
| 76-111 | `calcular`: pide ruta a API, aplica `config_tarifas`, muestra Q. |
| 113-125 | Actualiza mapa al cambiar combos. |
| 127-169 | Dibuja grafo y permite arrastrar con el mouse. |

### `cliente/vista_admin.py`

| Líneas | Qué hace |
|--------|----------|
| 9-34 | Resumen: cantidad municipios, tamaño matriz, estado API. |
| 36-52 | Listbox con los 49 municipios. |
| 54-70 | Campos para editar las 4 tarifas. |
| 81-96 | `guardar_configuracion_ui`: valida y guarda en `config_tarifas.py`. |

### `cliente/ui_helpers.py`

| Líneas | Qué hace |
|--------|----------|
| 6-11 | Constantes de colores y URL `http://localhost:5000`. |
| 14-31 | `ScrollableFrame`: formulario con scroll vertical. |
| 34-69 | Métodos `_panel`, `_titulo`, `_boton`, `_resultado`, etc. |

### `cliente/visualizador_grafo.py`

| Líneas | Qué hace |
|--------|----------|
| 9 | Ruta a `datos/grafo.drawio` para posiciones X,Y. |
| 14-19 | Normaliza nombres (tildes, mayúsculas). |
| 21-40 | Lee coordenadas de cada municipio del XML draw.io. |
| 42-51 | Construye grafo NetworkX desde la matriz. |
| 86-125 | Dibuja nodos, aristas, resalta ruta en rojo/azul. |
| 127-135 | Inserta el gráfico dentro del panel Tkinter. |

---

## 4. Demostración en vivo (5 minutos)

1. Terminal 1: `python api.py` → debe decir `API iniciada en http://localhost:5000`
2. Terminal 2: `python principal.py`
3. Cotizador: origen **GUATEMALA**, destino **LA ANTIGUA GUATEMALA**, peso **5**
4. Mostrar: ruta en rojo, km en azul, precio en rojo
5. Administrador: mostrar lista y `nucleo/config_tarifas.py`
6. Opcional: `curl http://localhost:5000/status`

---

## 5. Preguntas frecuentes del ingeniero

**¿Por qué cliente-servidor?**  
Cumple el requisito de separar responsabilidades: el servidor calcula rutas; el cliente cotiza y muestra UI.

**¿Por qué Flask?**  
Mismo patrón del curso: `@app.route`, `jsonify`, códigos HTTP 200/400/404.

**¿Dónde se editan los precios?**  
Solo en `nucleo/config_tarifas.py` (o desde Administrador, que escribe ese archivo).

**¿Qué algoritmo usan?**  
Floyd-Warshall: encuentra la distancia mínima entre **todos** los pares; luego se reconstruye la ruta.

**¿Qué pasa si la API está apagada?**  
El cliente muestra pantalla de error y botón **Intentar Reconectar**.

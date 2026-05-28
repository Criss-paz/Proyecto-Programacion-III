# Envíos Rápidos GT - Sistema de Rutas y Cotizaciones

Aplicación **cliente-servidor** en Python para cotizar envíos entre municipios de Guatemala usando **Floyd-Warshall**, API **Flask** e interfaz **Tkinter**.

> **Para exponer el proyecto:** lee [`docs/GUIA_EXPOSICION.md`](docs/GUIA_EXPOSICION.md) — orden de archivos y explicación línea por línea.

---

## Estructura del proyecto

```
├── api.py              → Inicia el servidor
├── principal.py        → Inicia el cliente
├── datos/              → Excel y diagrama del grafo
├── nucleo/             → Algoritmos, Excel y tarifas
├── servidor/           → API Flask
├── cliente/            → Interfaz gráfica
└── docs/               → Guía de exposición
```

---

## Ejecución

```bash
pip install -r requirements.txt
```

**Terminal 1 — API:**
```bash
python api.py
```

**Terminal 2 — Cliente:**
```bash
python principal.py
```

En VS Code: configuraciones **「1. Cliente」** y **「2. API」** en el depurador.

---

## API (Flask)

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/status` | Estado del servidor |
| GET | `/datos` | Municipios + matriz |
| GET | `/ruta?origen=X&destino=Y` | Km y ruta óptima |

---

## Tarifas

Archivo único: **`nucleo/config_tarifas.py`**

```
Precio = (Base + km×Q/km + lb×Q/lb) × (1 + margen)
```

Valores por defecto: Base Q15, Q0.35/km, Q1/lb, margen 30%.

---

## Tecnologías

Python 3.10+, Flask, pandas, NumPy, Tkinter, matplotlib, networkx, requests.

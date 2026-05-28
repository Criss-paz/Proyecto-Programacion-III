"""
API REST con Flask.
Expone municipios, matriz y rutas óptimas al cliente.
"""

from flask import Flask, jsonify, request
import numpy as np
from nucleo import lector_excel, algoritmos

app = Flask(__name__)
municipios, matriz = lector_excel.cargar_datos()


def _matriz_json():
    limpia = np.where(np.isinf(matriz) | np.isnan(matriz), 999, matriz)
    return limpia.tolist()


def _respuesta_ruta(origen, destino):
    if not origen or not destino:
        return {"error": "Parámetros 'origen' y 'destino' son requeridos."}, 400
    try:
        km, ruta = algoritmos.calcular_ruta_floyd(matriz, municipios, origen, destino)
    except ValueError as e:
        return {"error": str(e)}, 400
    if not np.isfinite(km):
        return {"km": None, "ruta": [], "error": "No existe una ruta disponible."}, 200
    return {"km": km, "ruta": ruta}, 200


@app.route("/datos", methods=["GET"])
def obtener_datos():
    return jsonify({"municipios": municipios, "matriz": _matriz_json()})


@app.route("/status", methods=["GET"])
def obtener_status():
    dim = list(matriz.shape) if matriz is not None and matriz.ndim == 2 else [0, 0]
    return jsonify({"status": "ok", "municipios_cargados": len(municipios), "matriz_dimension": dim})


@app.route("/ruta", methods=["GET"])
def obtener_ruta():
    cuerpo, codigo = _respuesta_ruta(request.args.get("origen", ""), request.args.get("destino", ""))
    return jsonify(cuerpo), codigo


@app.errorhandler(404)
def ruta_no_encontrada(_):
    return jsonify({"error": "Ruta no encontrada"}), 404


def iniciar(host="localhost", puerto=5000):
    print(f"API iniciada en http://{host}:{puerto}")
    app.run(host=host, port=puerto, debug=False)

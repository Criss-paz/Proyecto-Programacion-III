"""API REST del proyecto."""

import numpy as np
from flask import Flask, jsonify, request

from nucleo import algoritmos, lector_excel

app = Flask(__name__)
municipios, matriz = lector_excel.cargar_datos()


@app.route("/datos", methods=["GET"])
def obtener_datos():
    return jsonify({"municipios": municipios, "matriz": _matriz_para_json()})


@app.route("/status", methods=["GET"])
def obtener_status():
    return jsonify({
        "status": "ok",
        "municipios_cargados": len(municipios),
        "matriz_dimension": _dimension_matriz(),
    })


@app.route("/ruta", methods=["GET"])
def obtener_ruta():
    cuerpo, codigo = _calcular_ruta(
        request.args.get("origen", ""),
        request.args.get("destino", ""),
    )
    return jsonify(cuerpo), codigo


@app.errorhandler(404)
def ruta_no_encontrada(_):
    return jsonify({"error": "Ruta no encontrada"}), 404


def iniciar(host="127.0.0.1", puerto=5000):
    print(f"API iniciada en http://{host}:{puerto}")
    app.run(host=host, port=puerto, debug=False)


def _calcular_ruta(origen, destino):
    if not origen or not destino:
        return {"error": "Parametros 'origen' y 'destino' son requeridos."}, 400

    try:
        km, ruta = algoritmos.calcular_ruta_floyd(matriz, municipios, origen, destino)
    except ValueError as e:
        return {"error": str(e)}, 400

    if not np.isfinite(km):
        return {"km": None, "ruta": [], "error": "No existe una ruta disponible."}, 200
    return {"km": km, "ruta": ruta}, 200


def _matriz_para_json():
    matriz_limpia = np.where(np.isinf(matriz) | np.isnan(matriz), 999, matriz)
    return matriz_limpia.tolist()


def _dimension_matriz():
    if matriz is not None and matriz.ndim == 2:
        return list(matriz.shape)
    return [0, 0]

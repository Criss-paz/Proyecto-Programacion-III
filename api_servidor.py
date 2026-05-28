from flask import Flask, jsonify, request

import algoritmos
import lector_excel


app = Flask(__name__)

MUNICIPIOS, MATRIZ_DISTANCIAS = lector_excel.cargar_datos()


@app.route("/calcular_ruta", methods=["POST"])
def calcular_ruta():
    datos = request.get_json() or {}
    origen = datos.get("origen")
    destino = datos.get("destino")

    if not origen or not destino:
        return jsonify({"error": "Faltan datos de origen o destino"}), 400

    if origen == destino:
        return jsonify({"error": "El origen y el destino no pueden ser el mismo municipio"}), 400

    if len(MUNICIPIOS) == 0:
        return jsonify({"error": "No se cargaron datos desde el Excel"}), 500

    try:
        km_dijkstra, ruta_dijkstra = algoritmos.calcular_ruta_dijkstra(
            MATRIZ_DISTANCIAS,
            MUNICIPIOS,
            origen,
            destino,
        )
        km_floyd, ruta_floyd = algoritmos.calcular_ruta_floyd(
            MATRIZ_DISTANCIAS,
            MUNICIPIOS,
            origen,
            destino,
        )
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    respuesta = {
        "distancia_km": km_dijkstra,
        "ruta_optima": ruta_dijkstra,
        "distancia_dijkstra": km_dijkstra,
        "ruta_dijkstra": ruta_dijkstra,
        "distancia_floyd": km_floyd,
        "ruta_floyd": ruta_floyd,
        "mensaje": "Ruta calculada con datos reales desde la API",
    }

    return jsonify(respuesta), 200


if __name__ == "__main__":
    print("Iniciando API de Envios Rapidos GT...")
    print(f"Municipios cargados: {len(MUNICIPIOS)}")
    app.run(debug=True, port=5000)

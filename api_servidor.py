from flask import Flask, request, jsonify
import numpy as np
import lector_excel
import algoritmos

app = Flask(__name__)
municipios, matriz_original = lector_excel.cargar_datos()

if municipios:
    print("Calculando caminos mínimos con Floyd-Warshall...")
    matriz_min, matriz_rutas = algoritmos.aplicar_floyd_warshall(matriz_original)
    print("API lista en puerto 5000.")

@app.route('/calcular_ruta', methods=['POST'])
def calcular_ruta():
    datos = request.get_json()
    try:
        o, d = municipios.index(datos['origen']), municipios.index(datos['destino'])
        km = matriz_min[o][d]
        
        if not np.isfinite(km):
            return jsonify({"error": "No hay ruta terrestre disponible."}), 404
            
        return jsonify({
            "distancia_km": round(float(km), 2),
            "ruta_optima": algoritmos.obtener_ruta_minima(matriz_rutas, municipios, o, d)
        }), 200
        
    except ValueError:
        return jsonify({"error": "Municipio no válido."}), 400

if __name__ == '__main__':
    app.run(port=5000)
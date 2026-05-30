from flask import Flask, request, jsonify
import numpy as np
import lector_excel
import algoritmos
import config_tarifas

app = Flask(__name__)
municipios, matriz_original = lector_excel.cargar_datos()
ultimo_resultado = None

if municipios:
    print("Calculando caminos mínimos con Floyd-Warshall...")
    matriz_min, matriz_rutas = algoritmos.aplicar_floyd_warshall(matriz_original)
    print("API lista en puerto 5000.")

@app.route('/', methods=['GET'])
def inicio():
    if ultimo_resultado:
        return jsonify({
            "mensaje": "Ultima cotizacion calculada",
            "ultimo_resultado": ultimo_resultado
        }), 200

    return jsonify({
        "mensaje": "API Envios Rapidos GT activa",
        "endpoint": "/calcular_ruta",
        "metodos": {
            "GET": "Calcula una ruta usando parametros en la URL.",
            "POST": "Recibe JSON, calcula una cotizacion y la guarda como ultima cotizacion.",
            "PUT": "Recibe JSON, recalcula y reemplaza la ultima cotizacion.",
            "DELETE": "Elimina la ultima cotizacion guardada."
        },
        "recibe_json": {
            "origen": "Nombre del municipio de origen",
            "destino": "Nombre del municipio de destino",
            "peso": "Peso del paquete en libras"
        },
        "responde_json": {
            "exito": {
                "distancia_km": "Distancia de la ruta mas corta",
                "ruta_optima": ["Municipio origen", "Municipio intermedio", "Municipio destino"],
                "costo_empresa": "Costo interno del envio",
                "precio_final": "Total de la cotizacion para el cliente"
            },
            "error": {
                "error": "Mensaje indicando si no hay ruta o si el municipio no es valido"
            }
        }
    }), 200

@app.route('/calcular_ruta', methods=['GET', 'POST', 'PUT', 'DELETE'])
def calcular_ruta():
    global ultimo_resultado

    if request.method == 'DELETE':
        ultimo_resultado = None
        return jsonify({"mensaje": "Ultima cotizacion eliminada."}), 200

    if request.method == 'GET':
        datos = {
            "origen": request.args.get('origen'),
            "destino": request.args.get('destino'),
            "peso": request.args.get('peso')
        }
    else:
        datos = request.get_json(silent=True)

    if not datos or not datos.get('origen') or not datos.get('destino'):
        if request.method == 'GET':
            return jsonify({"error": "Debe enviar origen y destino en la URL."}), 400

        return jsonify({"error": "Debe enviar JSON con origen y destino."}), 400

    try:
        o, d = municipios.index(datos['origen']), municipios.index(datos['destino'])
        km = matriz_min[o][d]
        
        if not np.isfinite(km):
            return jsonify({"error": "No hay ruta terrestre disponible."}), 404
            
        respuesta = {
            "distancia_km": round(float(km), 2),
            "ruta_optima": algoritmos.obtener_ruta_minima(matriz_rutas, municipios, o, d)
        }

        if datos.get('peso') not in (None, ""):
            try:
                peso = float(datos['peso'])
            except ValueError:
                return jsonify({"error": "El peso debe ser numerico."}), 400

            tarifas = config_tarifas.obtener()
            costo = tarifas["COSTO_BASE"] + (tarifas["COSTO_POR_KM"] * km) + (tarifas["COSTO_POR_LIBRA"] * peso)
            precio = costo * (1 + tarifas["MARGEN_UTILIDAD"])
            respuesta["peso_libras"] = round(peso, 2)
            respuesta["costo_empresa"] = round(float(costo), 2)
            respuesta["precio_final"] = round(float(precio), 2)

        if request.method == 'PUT':
            respuesta["mensaje"] = "Cotizacion actualizada."
        elif request.method == 'POST':
            respuesta["mensaje"] = "Cotizacion creada."

        ultimo_resultado = respuesta
        return jsonify(respuesta), 200
        
    except ValueError:
        return jsonify({"error": "Municipio no válido."}), 400

if __name__ == '__main__':
    app.run(port=5000)

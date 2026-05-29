from flask import Flask, request, jsonify
import numpy as np
import lector_excel
import algoritmos

# 1. Inicializamos el servidor Flask
app = Flask(__name__)

print("====================================================")
print("INICIANDO SERVIDOR LOGÍSTICO - EMPRESA DE TRANSPORTES")
print("====================================================")

# 2. Carga Inicial de Datos (Se ejecuta una sola vez al encender la API)
print("[INFO] Cargando matriz de distancias desde el archivo Excel...")
municipios, matriz_original = lector_excel.cargar_datos()

if len(municipios) > 0:
    print("[INFO] Matriz cargada con éxito.")
    print("[INFO] Procesando caminos mínimos con el algoritmo de Floyd-Warshall...")
    # Ejecutamos el algoritmo sobre la matriz original y guardamos los resultados en memoria
    matriz_minima, matriz_recorrido = algoritmos.aplicar_floyd_warshall(matriz_original)
    print("[OK] ¡Algoritmo completado! API lista para escuchar peticiones en el puerto 5000.")
else:
    print("[ERROR] No se pudieron cargar los datos. Verifica que 'distancias.xlsx' esté en la carpeta.")

# 3. Endpoint que consultará la interfaz gráfica (Tkinter)
@app.route('/calcular_ruta', methods=['POST'])
def calcular_ruta():
    # Recibimos el JSON enviado por el cliente
    datos = request.get_json()
    origen = datos.get('origen')
    destino = datos.get('destino')

    # Validación de seguridad en la recepción
    if not origen or not destino:
        return jsonify({"error": "Faltan los datos obligatorios de origen o destino"}), 400

    try:
        # Limpiamos espacios en blanco invisibles y buscamos los índices en la lista
        idx_origen = municipios.index(origen.strip())
        idx_destino = municipios.index(destino.strip())

        # Extraemos la distancia mínima real calculada previamente por Floyd-Warshall
        kilometros = matriz_minima[idx_origen][idx_destino]

        # Reconstruimos la ruta exacta de los municipios por los que pasará el transporte
        ruta_exacta = algoritmos.obtener_ruta_minima(matriz_recorrido, municipios, idx_origen, idx_destino)

        # Si el resultado es 999, significa que físicamente no hay carreteras que conecten los puntos
        if not np.isfinite(kilometros):
            return jsonify({"error": "No existe una ruta terrestre disponible entre estos municipios"}), 404

        # Estructuramos la respuesta de vuelta al cliente
        respuesta = {
            "distancia_km": float(kilometros),
            "ruta_optima": ruta_exacta,
            "mensaje": "Cálculo real realizado con éxito desde el servidor."
        }
        
        print(f"[PETICIÓN] Envío cotizado con éxito: {origen} -> {destino} ({kilometros} km)")
        return jsonify(respuesta), 200

    except ValueError:
        return jsonify({"error": "Uno de los municipios seleccionados no existe en la matriz"}), 400
    except Exception as e:
        return jsonify({"error": f"Error interno en el servidor: {str(e)}"}), 500

# 4. Arranque de la aplicación local
if __name__ == '__main__':
    app.run(debug=True, port=5000)

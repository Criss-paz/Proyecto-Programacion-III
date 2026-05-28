from flask import Flask, request, jsonify

# NOTA PARA EL GRUPO: 
# Cuando el Integrante 2 termine sus algoritmos y el Excel esté listo, 
# descomentarán estas líneas para conectar los archivos:
# import lector_excel
# import algoritmos

# 1. Inicializamos la aplicación de Flask (El Servidor)
app = Flask(__name__)

# 2. Creamos la "Ruta" o "Endpoint" que el Cliente (Tkinter) va a consultar
@app.route('/calcular_ruta', methods=['POST'])
def calcular_ruta():
    
    # A. Recibimos el paquete de datos (JSON) que nos manda Tkinter
    datos = request.get_json()
    origen = datos.get('origen')
    destino = datos.get('destino')

    # B. Validación de seguridad básica
    if not origen or not destino:
        return jsonify({"error": "Faltan datos de origen o destino"}), 400

    print(f"Recibí una petición para calcular desde {origen} hacia {destino}")

    # C. --- ZONA DE CONEXIÓN (El trabajo pesado) ---
    # Aquí es donde llamarán a las funciones de sus compañeros.
    # Se vería algo así:
    # matriz_distancias = lector_excel.obtener_matriz()
    # kilometros, lista_nodos = algoritmos.dijkstra(matriz_distancias, origen, destino)
    
    # -> SIMULACIÓN (Mientras sus compañeros terminan el algoritmo) <-
    kilometros = 40.5
    lista_nodos = [origen, "Mixco", "San Lucas", destino]
    # ---------------------------------------------------------------

    # D. Empaquetamos la respuesta para enviársela de vuelta a Tkinter
    respuesta = {
        "distancia_km": kilometros,
        "ruta_optima": lista_nodos,
        "mensaje": "¡Ruta calculada con éxito desde el Servidor!"
    }

    return jsonify(respuesta), 200

# 3. Arrancamos el servidor
if __name__ == '__main__':
    print("Iniciando la API de la Empresa de Transporte...")
    # debug=True hace que el servidor se reinicie solo si le hacen cambios al código
    app.run(debug=True, port=5000)
import threading
from flask import Flask, Response, jsonify
from flask_cors import CORS
#Importacion de otras clases
from camara import SecuritySystem


app = Flask(__name__)
CORS(app)  # Habilita CORS para todas las rutas
sistema = SecuritySystem()

# Ruta para el stream de video
@app.route('/')
def video_feed():
    return Response(sistema.stream(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':  
      # Iniciamos en segundo plano el hilo que ejecuta la detección de seguridad
    hilo_deteccion = threading.Thread(target=sistema.run_detection, daemon=True)
    hilo_deteccion.start()
    # Iniciamos en segundo plano el hilo que verifica reportes periódicos
    hilo_reporte = threading.Thread(target=sistema.verify_report, daemon=True)
    hilo_reporte.start()
    # Iniciamos el servidor Flask
    app.run(debug=False, host='0.0.0.0', port=5000)
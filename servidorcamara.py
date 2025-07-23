import threading
from flask import Flask, Response, jsonify
from flask_cors import CORS
#Importacion de otras clases
from camara.camara import DetectionSystem
from ngrok_url_camara import ngrokurl

app = Flask(__name__)
CORS(app)  # Habilita CORS para todas las rutas
sistema = DetectionSystem()
p_url = ngrokurl(5000)  # Genera la URL pública

# Ruta para el stream de video
@app.route('/')
def video():
    return Response(sistema.stream(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Ruta para obtener la URL de Ngrok
@app.route('/get_ngrok_url')
def get_ngrok_url():
        if p_url.url_publica != "":
            return jsonify({"status": "success", "ngrok_url": f"{p_url.url_publica}/"})
        else:
            return "Nose pudo enviar la url."


if __name__ == '__main__':  
      # Iniciamos en segundo plano el hilo que ejecuta la detección de seguridad
    hilo_deteccion = threading.Thread(target=sistema.run_detection, daemon=True)
    hilo_deteccion.start()
    # Iniciamos el servidor Flask
    app.run(debug=False, host='0.0.0.0', port=5000)
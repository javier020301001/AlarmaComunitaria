import socket
from flask import Flask, Response, jsonify
from flask_cors import CORS
from camara import DetectionSystem
from pyngrok import ngrok
import os
import threading
import time

# --- Configuración inicial ---
app = Flask(__name__)
CORS(app)

# --- Clase para gestionar el servidor ---
class ServerManager:
    def __init__(self):
        self.sistema = DetectionSystem()
        self.ngrok_url = None
        self.port = self.find_available_port()

    def find_available_port(self, start_port=5001, end_port=5010):
        for port in range(start_port, end_port + 1):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('', port))
                    return port
            except OSError:
                continue
        raise Exception("No hay puertos disponibles")

    def run_flask(self):
        print(f"Iniciando Flask en puerto {self.port}")
        app.run(host='0.0.0.0', port=self.port, debug=False, use_reloader=False)

    def run_ngrok(self):
        self.ngrok_url = ngrok.connect(self.port).public_url
        print(f"Ngrok URL: {self.ngrok_url}")

    def generar_descripcion_video(self, video_path):
        import os
        if not os.path.exists(video_path):
            print(f"El archivo de video {video_path} no existe para procesar.")
            return "No se encontró un video local para procesar."
        try:
            from descripcionvideo import main
            # Cambiar el directorio de trabajo temporalmente si es necesario
            cwd = os.getcwd()
            video_dir = os.path.dirname(video_path)
            video_file = os.path.basename(video_path)
            if video_dir:
                os.chdir(video_dir)
            descripcion = main(video_file)  # Pasa el nombre del archivo directamente
            if video_dir:
                os.chdir(cwd)
            return descripcion
        except Exception as e:
            print(f"Error generando descripción del video: {e}")
            return "No se pudo generar una descripción precisa."

# --- Instancia del servidor ---
server = ServerManager()

# --- Rutas Flask ---
@app.route('/')
def video():
    return Response(
        server.sistema.stream(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

@app.route('/get_ngrok_url')
def get_ngrok_url():
    if server.ngrok_url:
        return jsonify({"status": "success", "url": server.ngrok_url})
    return jsonify({"status": "error", "message": "Ngrok no configurado"}), 500

@app.route('/ping')
def ping():
    return "pong"

@app.route('/disable_recording')
def disable_recording():
    server.sistema.disable_recording()
    return jsonify({"status": "success", "message": "Grabación deshabilitada"})

@app.route('/enable_recording')
def enable_recording():
    server.sistema.enable_recording()
    return jsonify({"status": "success", "message": "Grabación habilitada"})

@app.route('/video_feed')
def video_feed():
    return Response(
        server.sistema.stream(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

@app.route('/')
def index():
    return """
    <html>
      <body>
        <h1>Stream de Cámara</h1>
        <img src="/video_feed">
      </body>
    </html>
    """

# --- Main ---
if __name__ == '__main__':  
    # Hilo para Flask
    flask_thread = threading.Thread(target=server.run_flask, daemon=True)
    flask_thread.start()

    # Esperar que Flask esté listo
    time.sleep(2)

    # Ngrok (opcional, solo si lo necesitas)
    try:
        server.run_ngrok()
    except Exception as e:
        print(f"Ngrok no iniciado: {e}")

    # Hilo para detección
    detection_thread = threading.Thread(
        target=server.sistema.run_detection,
        daemon=True
    )
    detection_thread.start()

    # Mantener el programa activo
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🔌 Servidor detenido")
from flask import Flask, render_template, Response
from IPaddressClassification import SecuritySystem
import socket

app = Flask(__name__)
sistema = SecuritySystem()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video')
def video():
    return Response(sistema.generate_frame(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    local_ip = socket.gethostbyname(socket.gethostname())
    print(f"\n🌐 Accede desde esta máquina: http://127.0.0.1:5000")
    print(f"🌐 Accede desde otra máquina de la red: http://{local_ip}:5000\n")
    app.run(debug=False, host='0.0.0.0', port=5000)
















"""
from flask import Flask, render_template, Response, jsonify
from security_system import SecuritySystem
import socket
import threading
import time
import cv2

app = Flask(__name__)
sistema = SecuritySystem()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video')
def video():
    return Response(sistema.generate_frame(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/status')
def status():
    return jsonify({
        'status': sistema.status,
        'color': sistema.status_color,
        'last_event': sistema.last_event if sistema.last_event else "Ninguno",
        'device': sistema.device,
        'fps': round(sistema.fps, 1),
        'detections': sistema.last_detections_info
    })

def run_flask():
    app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)

if __name__ == '__main__':
    print("\n🛠️ Configuración del sistema de detección de robos:")
    print(f"- Dispositivo: {sistema.device}")
    print(f"- Resolución: {int(sistema.cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(sistema.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}")
    print(f"- FPS objetivo: {int(sistema.cap.get(cv2.CAP_PROP_FPS))}")
    print(f"- Sensibilidad: Conf={sistema.min_confidence}, Overlap={sistema.overlap_threshold}")
    print(f"- Clases de armas: {sistema.weapon_labels}")

    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    local_ip = socket.gethostbyname(socket.gethostname())
    print(f"\n🌐 Acceso web:")
    print(f"- Local: http://127.0.0.1:5000")
    print(f"- Red: http://{local_ip}:5000\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🔌 Apagando el sistema...")
        sistema.cleanup()
        print("✅ Sistema apagado correctamente")
    """
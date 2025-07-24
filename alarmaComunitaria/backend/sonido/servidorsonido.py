from flask import Flask, jsonify, request
import requests
from flask_cors import CORS

 
app = Flask(__name__)

CORS(app)
# Lista de dispositivos Android que simulan la alarma con Flask corriendo
dispositivos = [
    'http://172.20.10.5:5001/sonar'
]

@app.route('/activar_alarma', methods=['POST'])
def activar_alarma():
    try:
        for url in dispositivos:
            r = requests.get(url, timeout=5)
            r.raise_for_status()
        return jsonify({'status': 'ok', 'message': 'Alarma activada en todos los dispositivos'}), 200
    except requests.RequestException as e:
        return jsonify({'status': 'error', 'message': f'Error al activar alarma: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5020, debug=True)

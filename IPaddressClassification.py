from flask import Flask, render_template, Response
import cv2
import numpy as np
from ultralytics import YOLO
import os

app = Flask(__name__)

class SecuritySystem:
    def __init__(self):
        self.load_models()
        self.cap = self.setup_camera()
        self.status = "Todo en orden"
        self.status_color = (0, 255, 0)
        self.frame_count = 0
        self.yolo_interval = 6
        self.last_event = None

    def load_models(self):
        self.classNames = []
        classFile = 'coco.names'
        if os.path.exists(classFile):
            with open(classFile, 'rt') as f:
                self.classNames = f.read().rstrip('\n').split('\n')
        else:
            self.classNames = [f"Class_{i}" for i in range(90)]

        configPath = 'ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt'
        weightsPath = 'frozen_inference_graph.pb'

        if os.path.exists(configPath) and os.path.exists(weightsPath):
            self.net = cv2.dnn_DetectionModel(weightsPath, configPath)
            self.net.setInputSize(320, 320)
            self.net.setInputScale(1.0 / 127.5)
            self.net.setInputMean((127.5, 127.5, 127.5))
            self.net.setInputSwapRB(True)
        else:
            self.net = None

        try:
            self.yolo_model = YOLO('yolov8n.pt')  # Modelo ligero
            self.yolo_model.to('cuda' if cv2.cuda.getCudaEnabledDeviceCount() > 0 else 'cpu')
        except Exception as e:
            print(f"Error al cargar YOLOv8: {e}")
            self.yolo_model = None

    def setup_camera(self):
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        if not cap.isOpened():
            raise RuntimeError("No se pudo abrir la cámara")
        return cap

    def detect_events(self, frame):
        if self.yolo_model is None:
            return None

        small_frame = cv2.resize(frame, (320, 240))
        results = self.yolo_model(small_frame, verbose=False)[0]

        personas, armas = [], []
        x_scale = frame.shape[1] / small_frame.shape[1]
        y_scale = frame.shape[0] / small_frame.shape[0]

        for box in results.boxes:
            cls_id = int(box.cls)
            label = self.yolo_model.names[cls_id]
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            x1, y1, x2, y2 = int(x1 * x_scale), int(y1 * y_scale), int(x2 * x_scale), int(y2 * y_scale)

            if label == "person":
                personas.append((x1, y1, x2, y2))
            elif label in ["knife", "sports ball", "scissors", "gun"]:
                armas.append((x1, y1, x2, y2))

        for px1, py1, px2, py2 in personas:
            for ax1, ay1, ax2, ay2 in armas:
                pc = ((px1 + px2) // 2, (py1 + py2) // 2)
                ac = ((ax1 + ax2) // 2, (ay1 + ay2) // 2)
                if np.linalg.norm(np.array(pc) - np.array(ac)) < 150:
                    return "robo"
        return None

    def detect_covered_camera(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        avg_brightness = cv2.mean(gray)[0]
        std_dev = np.std(gray)
        threshold = max(20, 50 - std_dev)
        return avg_brightness < threshold

    def generate_frame(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            if self.net is not None:
                classIds, confs, bbox = self.net.detect(frame, confThreshold=0.5)
                if classIds is not None:
                    for classId, confidence, box in zip(classIds.flatten(), confs.flatten(), bbox):
                        cv2.rectangle(frame, box, (0, 255, 0), 2)
                        cv2.putText(frame, f"{self.classNames[classId - 1]} {int(confidence * 100)}%",
                                    (box[0], box[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            self.frame_count += 1
            if self.frame_count % self.yolo_interval == 0:
                self.last_event = self.detect_events(frame)

            evento = self.last_event

            self.status = "Todo en orden"
            self.status_color = (0, 255, 0)

            if self.detect_covered_camera(frame):
                evento = "cámara_tapada"
                self.status = "❌ Cámara tapada"
                self.status_color = (0, 0, 255)
            elif evento == "robo":
                self.status = "🚨 ¡Alerta de robo!"
                self.status_color = (0, 0, 255)

            cv2.putText(frame, self.status, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, self.status_color, 2)

            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                continue
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

# Instancia global del sistema
system = SecuritySystem()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video')
def video():
    return Response(system.generate_frame(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=False, threaded=True)

"""
K003nMvEnqGfhdnRoNGRFTKSdD0xyxs
"""
from collections import deque
from threading import Thread
import cv2, requests, os, time
from ultralytics import YOLO
from datetime import datetime
from APIgemini import Answer
from b2sdk.v2 import InMemoryAccountInfo, B2Api

class DetectionSystem:
    def __init__(self):
        self.load_models()        
        self.cap = self.setup_camera()
        # Estado de la camara
        self.status = "Camara operativa"
        self.status_anterior = None
        self.alert = "Todo en orden"
        self.alert_color = (0, 255, 0)
        self.ultimo_frame = None
        self.running = True
        # Datos de la camara 
        self.camara_name = "Camara Principal"
        self.ubicacion = {"lat": -0.0626, "lon": -78.4516} # Modificar manualmente
        # Grabacion
        self.recording = False
        self.video_writer = None
        self.recording_start_time = None
        self.fps = 5
        self.frames_buffer = deque(maxlen=self.fps * 10)

        # Credenciales de Backblaze 
        self.b2_bucket = "AlarmaComunitaria"
        self.b2_id = "003cd05bb9dad300000000002"
        self.b2_key = "K003nMvEnqGfhdnRoNGRFTKSdD0xyxs"
        self.setup_backblaze()

    # Carga los modelos
    def load_models(self): 
        self.model_armas = YOLO('./modelos/detect/Normal_Compressed/weights/best.pt')
        self.model_personas = YOLO('./modelos/yolov8n.pt')
        print("Modelos cargados correctamente.")

    # Configuracion de la camara
    def setup_camera(self):
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not cap.isOpened():
            print("Error: No se pudo abrir la cámara")
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        return cap

    # COmenzar la grabacion
    def start_recording(self):            
        now = datetime.now()
        self.current_filename = f"alert_{now.strftime('%Y%m%d_%H%M%S')}.mp4"
        fourcc = cv2.VideoWriter_fourcc(*'avc1')
        frame_size = (640, 480)
        self.video_writer = cv2.VideoWriter(self.current_filename, fourcc, self.fps, (640, 480))
        for frame in self.frames_buffer:
            self.video_writer.write(frame)
        
        self.recording = True
        self.recording_start_time = time.time()
        print(f"Iniciando grabación.")
    
    # Dtener grabacion
    def stop_recording(self):    
        self.recording = False
        self.video_writer.release()
        print(f"Grabación del video {self.current_filename} completa.")
        Thread(target=self.upload_to_backblaze_sent_alert, args=(self.current_filename,), daemon=True).start()
    
    # Autenticacion a backblaze
    def setup_backblaze(self):
        info = InMemoryAccountInfo()
        self.b2_api = B2Api(info)
        # Autoriza la cuenta
        self.b2_api.authorize_account("production", self.b2_id, self.b2_key)
        # Obtiene el bucket
        self.bucket = self.b2_api.get_bucket_by_name(self.b2_bucket)
        print("Conexión con Backblaze B2 establecida correctamente")
    
    # Carga video y enviar los datos
    def upload_to_backblaze_sent_alert(self, filename):
        print(f"Subiendo {filename} a Backblaze B2")
        self.bucket.upload_local_file(local_file=filename, file_name=filename)
        print(f"Video {filename} subido exitosamente")
        url_video = f"https://f003.backblazeb2.com/file/{self.b2_bucket}/{filename}"
        # Guardar la URL en un archivo para que otro archivo la lea
        with open("ultima_url.txt", "w") as f:
            f.write(url_video)
        # Borrar archivo local después de subir
        os.remove(filename)
        descripcion = Answer()
        # Datos de la camara
        detalle = {
            "nombre_camara": self.camara_name,
            "ubicacion": self.ubicacion,
            "fecha": datetime.now().isoformat(),
            "alerta": "Peligro, intento sospechoso!!!",
            "informacion_extra": {
                "Descripcion": descripcion,
                "Evidencia": url_video
            }
        }
        requests.post("http://localhost:8000/api/detalle", json=detalle)

    # Deteccion de armas y peronas 
    def detect_events(self, frame):
        if self.model_personas is None or self.model_armas is None:
            return None
        self.personas_detectadas = 0
        self.armas_detectadas = 0

        # Detección de personas
        resultados_p = self.model_personas(frame, classes=[0], conf=0.6, verbose=False)
        for det in resultados_p:
            for box in det.boxes:
                self.personas_detectadas += 1
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                cv2.putText(frame, "Persona", (x1, y1 - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

        # Detección de armas solo si hay personas
        if self.personas_detectadas > 0:
            resultados_a = self.model_armas(frame, conf=0.6, verbose=False)
            for det in resultados_a:
                for box in det.boxes:
                    self.armas_detectadas += 1
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                    cv2.putText(frame, "Arma", (x1, y1 - 10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        # Verificar condición de peligro
        if self.personas_detectadas >= 1 and self.armas_detectadas >= 1:
            return "peligro"
        return None
    
    # Informacion agregada a la camara
    def add_overlay(self, frame):
        # Obtener fecha y hora actual
        now = datetime.now()
        fecha_hora = now.strftime("%d/%m/%Y %H:%M:%S")
        overlay = frame
        # Añadir fondo semitransparente para la información
        cv2.rectangle(overlay, (0, 0), (640, 80), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)
        
        # Mostrar información en la parte superior
        cv2.putText(frame, f"{self.camara_name}", (20, 30), 
        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, f"Estado: {self.alert}", (20, 60),
        cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.alert_color, 2)
        
        # Mostrar contadores en la parte inferior
        cv2.rectangle(frame, (0, 410), (640, 900), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)
        cv2.putText(frame, f"Fecha y Hora: {fecha_hora}", (20, 460), 
        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    # Metodo que realiza la deteccion
    def run_detection(self):
        self.enviar_estado()
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                if self.status != "Camara desconectada":
                    self.status = "Camara desconectada"
                    self.enviar_estado()
                time.sleep(0.1)
                continue
            else:
                if self.status != "Camara operativa":
                    self.status = "Camara operativa"
                    self.enviar_estado()

            frame_sin_procesar = frame.copy()
            self.frames_buffer.append(frame_sin_procesar)
            evento = self.detect_events(frame)
            self.alert = "Todo en orden"
            self.alert_color = (0, 255, 0)
            if evento == "peligro":
                self.alert = "Peligro, intento sospechoso!!!"
                self.alerts_color = (0, 0, 255)
                if not self.recording:
                    self.start_recording()

            if self.recording:
                self.video_writer.write(frame_sin_procesar)
                
                if time.time() - self.recording_start_time >= 10:
                    self.stop_recording()
                
            # Añadir overlay con información
            self.add_overlay(frame)
            self.ultimo_frame = frame

    # Envio de estado de la camara
    def enviar_estado(self):
        if self.status != self.status_anterior:
            requests.post("http://localhost:8000/api/estado", json={"status": self.status})
            print(f"{self.status}.")
            self.status_anterior = self.status

    # Streaming para flask
    def stream(self):
        while True:
            if self.ultimo_frame is None:
                time.sleep(0.001)
                continue
            resultado, buffer = cv2.imencode('.jpg', self.ultimo_frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

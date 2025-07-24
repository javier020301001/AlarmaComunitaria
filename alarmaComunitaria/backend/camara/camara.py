"""
K003nMvEnqGfhdnRoNGRFTKSdD0xyxs
"""
from threading import Thread, Lock
import cv2, requests, os, time
from ultralytics import YOLO
from datetime import datetime
from descripcionvideo import main,Answer
from b2sdk.v2 import InMemoryAccountInfo, B2Api
import numpy as np
import atexit
import json

class DetectionSystem:
    def __init__(self):
        # Cargamos los modelos de detección y preparar todo al iniciar
        self.load_models()        
        self.cap = self.setup_camera()
        # Variables de estado
        self.status = "Camara operativa"
        self.status_anterior = None
        self.alert = "Todo en orden"
        self.alert_color = (0, 255, 0)
        self.ultimo_frame = None
        self.running = True
        self.camara_name = "Camara Principal"
        # Inicializar ubicación por defecto
        self.ubicacion = {"lat": 0, "lon": 0}
        # Variables para grabar video
        self.recording = False
        # Evitar grabar mientras se sube
        self.uploading = False     
        # Control de grabación - deshabilitada cuando se muestra en frontend
        self.recording_enabled = True
        self.video_writer = None
        self.fps = 5
        self.recording_lock = Lock()
        self.recording_duration = 10
        self.recording_frames_remaining = 0
        self.detection_active = False
        # Configuración de Backblaze
        self.b2_bucket = "AlarmaComunitaria"
        self.b2_id = "003cd05bb9dad300000000002"
        self.b2_key = "K003nMvEnqGfhdnRoNGRFTKSdD0xyxs"
        self.setup_backblaze()
        # Obtener ubicación por IP (solo una vez)
        ubicacion_obtenida = self.get_location_by_ip()
        # Solo registrar la cámara si se pudo obtener la ubicación real
        self.camara_registrada = False
        if ubicacion_obtenida:
            self.registrar_camara_en_backend()
            self.camara_registrada = True
        else:
            print("No se registró la cámara en el backend porque no se pudo obtener la ubicación real.")
        # Eliminar la cámara del backend al cerrar
        atexit.register(self.eliminar_camara_en_backend)

    # Carga los modelos de detección de armas y personas
    def load_models(self): 
        self.model_armas = YOLO('C:/Users/JAVIER/Downloads/AlarmaComunitariaCompleto/alarmaComunitaria/backend/camara/modelos/detect/Normal_Compressed/weights/best.pt')
        self.model_personas = YOLO('C:/Users/JAVIER/Downloads/AlarmaComunitariaCompleto/alarmaComunitaria/backend/camara/modelos/modelos/yolov8n.pt')
        print("Modelos cargados correctamente.")

    # Inicializa la cámara web
    def setup_camera(self):
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not cap.isOpened():
            print("Error: No se pudo abrir la cámara")
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        return cap

    # Método para deshabilitar la grabación (cuando se muestra en frontend)
    def disable_recording(self):
        self.recording_enabled = False
        print("📹 Grabación deshabilitada - Cámara visible en frontend")
    
    # Método para habilitar la grabación (cuando se oculta del frontend)
    def enable_recording(self):
        self.recording_enabled = True
        print("📹 Grabación habilitada - Cámara oculta del frontend")

    # Empieza a grabar el video
    def start_recording(self):            
        with self.recording_lock:
            if self.recording or self.uploading:  # <- también comprobamos si está subiendo
                return
            # Verificar si la grabación está habilitada
            if not self.recording_enabled:
                print("📹 Grabación cancelada - Cámara visible en frontend")
                return
            now = datetime.now()
            self.current_filename = f"alert_{now.strftime('%Y%m%d_%H%M%S')}.mp4"
            fourcc = cv2.VideoWriter_fourcc(*'avc1')
            self.video_writer = cv2.VideoWriter(self.current_filename, fourcc, self.fps, (640, 480))
            self.recording = True
            self.recording_frames_remaining = self.fps * self.recording_duration
            print(f"Iniciando grabación de {self.recording_duration} segundos.")

    # Detiene la grabación y sube el video a la nube
    def stop_recording(self):
        with self.recording_lock:
            if not self.recording:
                return
            self.video_writer.release()
            self.recording = False
            self.uploading = True      # <- marcamos que empieza el upload
            print(f"Grabación completada: {self.current_filename}")

            Thread(
                target=self.upload_to_backblaze_sent_alert,
                args=(self.current_filename,),
                daemon=True
            ).start()

    # Conexión con la nube (Backblaze B2)
    def setup_backblaze(self):
        info = InMemoryAccountInfo()
        self.b2_api = B2Api(info)
        self.b2_api.authorize_account("production", self.b2_id, self.b2_key)
        self.bucket = self.b2_api.get_bucket_by_name(self.b2_bucket)
        print("Conexión con Backblaze B2 establecida correctamente")

    # Sube el video a la nube y envía un reporte al servidor
    def upload_to_backblaze_sent_alert(self, filename):
        print(f"Subiendo {filename} a Backblaze B2")
        self.bucket.upload_local_file(local_file=filename, file_name=filename)
        print(f"Video {filename} subido exitosamente")
        url_video = f"https://f003.backblazeb2.com/file/{self.b2_bucket}/{filename}"
        # Guarda la URL del video en un archivo
        with open("ultima_url.txt", "w") as f:
            f.write(url_video)
        # Borra el archivo local
        os.remove(filename)
        
        # obtener descripción y enriquecerla con manejo de errores
        try:
            descripcion = main()
            descripcion_f = Answer(descripcion)
        except Exception as e:
            if "quota" in str(e).lower() or "429" in str(e) or "ResourceExhausted" in str(e):
                print("Cuota de Gemini API agotada. Usando descripción básica.")
                descripcion_f = "Análisis no disponible - cuota agotada"
            else:
                print(f"Error en análisis: {e}")
                descripcion_f = "Error en análisis del video"
        
        # solo enviar si contiene la frase clave
        if "Inseguridad" in descripcion_f:
            detalle = {
                "nombre_camara": self.camara_name,
                "ubicacion": self.ubicacion,
                "fecha": datetime.now().isoformat(),
                "alerta": "Peligro, intento sospechoso!!!",
                "informacion_extra": {
                    "Descripcion": descripcion_f,
                    "Evidencia": url_video
                }
            }
            try:
                response = requests.post("http://localhost:3000/api/notifications/detalle", json=detalle)
                if response.status_code == 200:
                    print("Notificación enviada al servidor exitosamente.")
                else:
                    print(f"Error al enviar notificación. Código: {response.status_code}")
            except Exception as e:
                print(f"Error de conexión al servidor: {e}")
        else:
            print("ℹNo se detectó inseguridad confirmada. Notificación NO enviada.")

        with self.recording_lock:
            self.uploading = False

    # Aquí se detectan las personas y armas en el frame
    def detect_events(self, frame):
        if self.model_personas is None or self.model_armas is None:
            return None
        self.personas_detectadas = 0
        self.armas_detectadas = 0
        self.personas_boxes = []
        self.armas_boxes = []
        # Detección de personas
        resultados_p = self.model_personas(frame, classes=[0], conf=0.6, verbose=False)
        for det in resultados_p:
            for box in det.boxes:
                self.personas_detectadas += 1
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                self.personas_boxes.append((x1, y1, x2, y2))
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                cv2.putText(frame, "Persona", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
        # Detección de armas
        resultados_a = self.model_armas(frame, conf=0.6, verbose=False)
        for det in resultados_a:
            for box in det.boxes:
                self.armas_detectadas += 1
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                self.armas_boxes.append((x1, y1, x2, y2))
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                cv2.putText(frame, "Arma", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        # Condiciones para activar alerta
        condicion_activa = False
        # Si hay dos personas muy cerca
        if self.personas_detectadas >= 2:
            for i in range(len(self.personas_boxes)):
                for j in range(i+1, len(self.personas_boxes)):
                    x1_i, y1_i, x2_i, y2_i = self.personas_boxes[i]
                    x1_j, y1_j, x2_j, y2_j = self.personas_boxes[j]
                    centro_i = ((x1_i + x2_i) // 2, (y1_i + y2_i) // 2)
                    centro_j = ((x1_j + x2_j) // 2, (y1_j + y2_j) // 2)
                    distancia = ((centro_i[0] - centro_j[0])**2 + (centro_i[1] - centro_j[1])**2)**0.5
                    if distancia < 150:
                        condicion_activa = True
                        cv2.line(frame, centro_i, centro_j, (0, 255, 255), 2)
                        cv2.putText(frame, f"Distancia: {int(distancia)}", 
                                    (centro_i[0] + 10, centro_i[1]), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
        if self.armas_detectadas >= 1:
            condicion_activa = True
        if self.personas_detectadas > 2:
            condicion_activa = True
        if condicion_activa:
            if not self.detection_active:
                self.detection_active = True
                return "peligro"
        else:
            self.detection_active = False   
        return None

    # Pone texto y fondo negro arriba y abajo del video con info útil
    def add_overlay(self, frame):
        now = datetime.now()
        fecha_hora = now.strftime("%d/%m/%Y %H:%M:%S")
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (640, 80), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)

        cv2.putText(frame, f"{self.camara_name}", (20, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, f"Estado: {self.alert}", (20, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.alert_color, 2)

        cv2.rectangle(frame, (0, 410), (640, 900), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)
        cv2.putText(frame, f"Fecha y Hora: {fecha_hora}", (20, 460), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    # Bucle principal: captura frames, detecta eventos, graba y actualiza estado
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
            evento = self.detect_events(frame)

            self.alert = "Todo en orden"
            self.alert_color = (0, 255, 0)

            if evento == "peligro":
                self.alert = "Peligro, intento sospechoso!!!"
                self.alert_color = (0, 0, 255)
                self.start_recording()

            if self.recording:
                self.video_writer.write(frame_sin_procesar)
                self.recording_frames_remaining -= 1
                if self.recording_frames_remaining <= 0:
                    self.stop_recording()

            self.add_overlay(frame)
            self.ultimo_frame = frame

    # Enviar estado de la cámara al servidor sólo si cambió
    def enviar_estado(self):
        if self.status != self.status_anterior:
            try:
                # Nota: Esta ruta no existe en tu backend actual
                # Deberías crear el endpoint /api/notifications/estado en tu backend
                response = requests.post("http://localhost:3000/api/notifications/estado", 
                                       json={"status": self.status}, timeout=5)
                if response.status_code == 200:
                    print(f"Estado enviado: {self.status}")
                else:
                    print(f"Error al enviar estado. Código: {response.status_code}")
            except requests.exceptions.ConnectionError:
                print(f"🌐 No se pudo conectar al servidor para enviar estado: {self.status}")
            except requests.exceptions.Timeout:
                print(f"Timeout al enviar estado: {self.status}")
            except Exception as e:
                print(f"Error al enviar estado: {e}")
            
            self.status_anterior = self.status

    # Permite enviar el último frame a un navegador o cliente como MJPEG
    def stream(self):
        while True:
            if self.ultimo_frame is None:
                time.sleep(0.001)
                continue
            resultado, buffer = cv2.imencode('.jpg', self.ultimo_frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    # Nuevo método para obtener ubicación por IP
    def get_location_by_ip(self):
        try:
            print("Obteniendo ubicación por IP...")
            response = requests.get('https://ipinfo.io/json', timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'loc' in data:
                    lat, lon = map(float, data['loc'].split(','))
                    # Actualizar la ubicación con los valores reales
                    self.ubicacion = {"lat": lat, "lon": lon}
                    print(f"Ubicación obtenida por IP: {self.ubicacion}")
                    return True
                else:
                    print("No se encontró información de ubicación en la respuesta de ipinfo.io")
            else:
                print(f"Error al obtener ubicación por IP: {response.status_code}")
        except requests.exceptions.Timeout:
            print("Timeout al obtener ubicación por IP. Usando ubicación por defecto.")
        except requests.exceptions.ConnectionError:
            print("Error de conexión al obtener ubicación por IP. Usando ubicación por defecto.")
        except Exception as e:
            print(f"No se pudo obtener la ubicación por IP. Usando ubicación por defecto. Error: {e}")
        
        # Si no se pudo obtener la ubicación, mantener la por defecto
        print(f"📍 Usando ubicación por defecto: {self.ubicacion}")
        return False

    # Nuevo método para registrar la cámara como punto en el backend
    def registrar_camara_en_backend(self):
        try:
            print(f"📡 Registrando cámara en el backend con ubicación: {self.ubicacion}")
            # userId genérico
            usuario_id = "camara-generica"
            punto = {
                "tipo": "camara",
                "lat": self.ubicacion["lat"],
                "lng": self.ubicacion["lon"],
                "titulo": self.camara_name,
                "descripcion": "Cámara de seguridad activa",
                "usuarioId": usuario_id
            }
            response = requests.post("http://localhost:3000/api/puntos", json=punto, timeout=10)
            if response.status_code == 201:
                print("Cámara registrada exitosamente en el mapa del backend.")
            else:
                print(f"No se pudo registrar la cámara en el backend. Código: {response.status_code}")
                print(f"Respuesta: {response.text}")
        except requests.exceptions.ConnectionError:
            print("Error de conexión al registrar la cámara en el backend.")
        except requests.exceptions.Timeout:
            print("Timeout al registrar la cámara en el backend.")
        except Exception as e:
            print(f"Error registrando la cámara en el backend: {e}")

    # Nuevo método para eliminar la cámara como punto en el backend
    def eliminar_camara_en_backend(self):
        # Solo eliminar si la cámara fue registrada
        if not hasattr(self, 'camara_registrada') or not self.camara_registrada:
            print("ℹNo se elimina la cámara del backend porque no fue registrada.")
            return
            
        try:
            print(f"Eliminando cámara del backend: {self.camara_name}")
            # userId genérico y nombre de cámara para identificar el punto
            usuario_id = "camara-generica"
            params = {
                "usuarioId": usuario_id,
                "titulo": self.camara_name
            }
            response = requests.delete("http://localhost:3000/api/puntos", params=params, timeout=10)
            if response.status_code == 200:
                print("Cámara eliminada exitosamente del mapa del backend.")
            else:
                print(f"⚠️ No se pudo eliminar la cámara del backend. Código: {response.status_code}")
                print(f"Respuesta: {response.text}")
        except requests.exceptions.ConnectionError:
            print("Error de conexión al eliminar la cámara del backend.")
        except requests.exceptions.Timeout:
            print("Timeout al eliminar la cámara del backend.")
        except Exception as e:
            print(f"Error eliminando la cámara del backend: {e}")
# Alarma Comunitaria – Sistema de Detección y Alerta en Tiempo Real

# Descripción General
Alarma Comunitaria es un sistema integral de videovigilancia inteligente que detecta situaciones de peligro (como la presencia de armas o comportamientos sospechosos) en tiempo real usando modelos de inteligencia artificial (YOLOv8 y Gemini AI). El sistema graba evidencia en video, la sube automáticamente a la nube (Backblaze B2), genera una descripción automática del evento y notifica a los usuarios conectados mediante una interfaz web y notificaciones en tiempo real.


# Características Principales
- Detección automática de armas y persona usando modelos YOLOv8.
- Grabación de video Solo cuando se detecta una situación de peligro.
- Subida automática de videos a la nube (Backblaze B2) para resguardo y consulta.
- Generación de descripciones automáticas de los eventos usando IA (Gemini de Google).
- Notificaciones en tiempo real a usuarios conectados mediante WebSockets.
- Interfaz web para monitoreo y visualización de alertas (Prueba).
- Geolocalización de cámaras y usuarios para alertas personalizadas.


# Estructura del Proyecto
AlarmaComunitariaBackEndv3.2/
│
├── camara/                  # Lógica de detección y gestión de cámara
│   └── camara.py
├── descripcionvideo.py      # Procesamiento y descripción automática de videos
├── ngrok_url_camara.py      # Gestión de túneles públicos con ngrok
├── preprocessing_images.py  # Utilidades de procesamiento de imágenes
├── servidorcamara.py        # Servidor principal de la cámara (detección y streaming)
├── servidornotificaciones.py# Servidor de notificaciones y gestión de usuarios
├── templates/
│   └── index.html           # Interfaz web de monitoreo
├── ultima_url.txt           # Última URL de video subido
├── requirements.txt         # Dependencias del proyecto
└── README.md                # Este archivo


# Instalación
1. Clona el repositorio:
   git clone <URL-del-repositorio>
   cd AlarmaComunitariaBackEndv3.2

2. Instala las dependencias:
   pip install -r requirements.txt

3. Configura los modelos YOLOv8:
   - Coloca los archivos de pesos (`best.pt`, `yolov8n.pt`, etc.) en las rutas indicadas en `camara/camara.py`.

4. Configura las credenciales de Backblaze B2:
   - Las credenciales están en el código, pero puedes cambiarlas por seguridad.


# Ejecución
1. Inicia el servidor de notificaciones:
   python servidornotificaciones.py

2. Inicia el servidor de la cámara:
   python servidorcamara.py

3. Accede a la interfaz web:
   - Abre `templates/index.html` en tu navegador o accede a la URL pública generada por ngrok (se mostrará en consola).

4. Prueba el sistema:
   - Realiza una acción sospechosa frente a la cámara (por ejemplo, muestra un cuchillo) y observa cómo se graba el video, se sube a la nube y se notifica a los usuarios.


# Detalles Técnicos
- Detección: Se realiza en tiempo real usando OpenCV y modelos YOLOv8.
- Almacenamiento en la nube: Los videos se suben automáticamente a Backblaze B2.
- Descripción automática: Se usa Gemini AI para analizar el video y generar una descripción textual del evento.
- Notificaciones: Se envían mediante Flask-SocketIO a todos los usuarios conectados.
- Geolocalización: Los usuarios y cámaras pueden ser geolocalizados para alertas personalizadas.


# Seguridad
- Las credenciales de Backblaze están actualmente en el código para pruebas. Cámbialas antes de usar en producción.
- El sistema puede ser extendido para autenticación de usuarios y cifrado de datos.


# Créditos y Licencia
Desarrollado por [Grupo6, Javier Saransig, Carlos Patiño y Luis Achig ].  
Basado en modelos YOLOv8 y Gemini AI.  

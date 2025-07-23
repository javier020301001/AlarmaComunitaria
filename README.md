# 🚨 Alarma Comunitaria – Detección y Alerta en Tiempo Real

Sistema inteligente de videovigilancia que detecta armas y situaciones de peligro usando IA (YOLOv8 + Gemini), graba evidencia, la sube a la nube y notifica en tiempo real a los usuarios. Incluye interfaz web para monitoreo y alertas.

---

## 📝 Requisitos

- Python 3.10 o superior
- Cámara web conectada
- Cuenta en Backblaze B2 (para almacenamiento en la nube)
- Modelos YOLOv8 entrenados (`best.pt`, `yolov8n.pt`, etc.)
- Conexión a Internet

---

## 📦 Instalación

1. **Clona el repositorio**
   ```bash
   git clone <URL-del-repositorio>
   cd AlarmaComunitariaBackEndv3.2
   ```

2. **(Opcional) Crea y activa un entorno virtual**
   ```bash
   python -m venv .venv
   # En Windows:
   .venv\Scripts\activate
   # En macOS/Linux:
   source .venv/bin/activate
   ```

3. **Instala las dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configura los modelos YOLOv8**
   - Coloca los archivos de pesos (`best.pt`, `yolov8n.pt`, etc.) en las rutas indicadas en `camara/camara.py`.

5. **Configura las credenciales de Backblaze B2**
   - Edita las variables en el código o usa variables de entorno para mayor seguridad.

---

## 🚀 Uso

1. **Inicia el servidor de notificaciones**
   ```bash
   python servidornotificaciones.py
   ```

2. **Inicia el servidor de la cámara**
   ```bash
   python servidorcamara.py
   ```

3. **Abre la interfaz web**
   - Abre `templates/index.html` en tu navegador o accede a la URL pública generada por ngrok (se mostrará en consola).

4. **Prueba el sistema**
   - Realiza una acción sospechosa frente a la cámara (por ejemplo, muestra un cuchillo) y observa cómo se graba el video, se sube a la nube y se notifica a los usuarios.

---

## 🎯 Características Principales

- **Detección automática de armas y personas** usando modelos YOLOv8.
- **Grabación de video** solo cuando se detecta una situación de peligro.
- **Subida automática de videos** a la nube (Backblaze B2) para resguardo y consulta.
- **Generación de descripciones automáticas** de los eventos usando IA (Gemini de Google).
- **Notificaciones en tiempo real** a usuarios conectados mediante WebSockets.
- **Interfaz web** para monitoreo y visualización de alertas.
- **Geolocalización** de cámaras y usuarios para alertas personalizadas.

---

## 📂 Estructura del proyecto

```
AlarmaComunitariaBackEndv3.2/
├── camara/                # Lógica de detección y gestión de cámara
│   └── camara.py
├── descripcionvideo.py    # Procesamiento y descripción automática de videos
├── ngrok_url_camara.py    # Gestión de túneles públicos con ngrok
├── preprocessing_images.py# Utilidades de procesamiento de imágenes
├── servidorcamara.py      # Servidor principal de la cámara
├── servidornotificaciones.py # Servidor de notificaciones y usuarios
├── templates/
│   └── index.html         # Interfaz web de monitoreo
├── ultima_url.txt         # Última URL de video subido
├── requirements.txt       # Dependencias del proyecto
└── README.md
```

---

## ⚙️ Detalles Técnicos

- **Detección:** Se realiza en tiempo real usando OpenCV y modelos YOLOv8.
- **Almacenamiento en la nube:** Los videos se suben automáticamente a Backblaze B2.
- **Descripción automática:** Se usa Gemini AI para analizar el video y generar una descripción textual del evento.
- **Notificaciones:** Se envían mediante Flask-SocketIO a todos los usuarios conectados.
- **Geolocalización:** Los usuarios y cámaras pueden ser geolocalizados para alertas personalizadas.

---

## 🛠️ Personalizaciones

- Cambia los modelos YOLOv8 por otros entrenados si lo deseas.
- Ajusta la duración de grabación, umbrales de detección y rutas en `camara/camara.py`.
- Puedes mejorar la interfaz web editando `templates/index.html`.

---

## 🔒 Seguridad

- Las credenciales de Backblaze están actualmente en el código para pruebas. **Cámbialas antes de usar en producción.**
- El sistema puede ser extendido para autenticación de usuarios y cifrado de datos.

---

## 🤝 Contribuciones

¿Quieres mejorar el sistema?
Haz un fork, crea una rama y envía tu pull request. ¡Toda contribución es bienvenida!

---

## 📄 Licencia

Este proyecto está bajo la licencia MIT.

---

## 👨‍💻 Créditos

Desarrollado por Grupo6: Javier Saransig, Carlos Patiño y Luis Achig.
Basado en modelos YOLOv8 y Gemini AI.


# 🚨 Kuntur Alarma Comunitaria

Es un sistema inteligente de videovigilancia y alerta en tiempo real, nacido como un prototipo ante la alta inseguridad que atraviesa Ecuador. Es una propuesta en desarrollo, pensada para madurar y adaptarse a las necesidades de la comunidad.

---

## 📝 Origen

Kuntur nació como respuesta a la creciente inseguridad en Ecuador. Es una propuesta desarrollada en la materia de Desarrollo de Sistemas de Información, bajo la dirección del tutor. Se trata de un prototipo funcional que busca demostrar cómo la tecnología puede ayudar a la comunidad, aunque aún requiere mejoras y maduración para su uso masivo.

---

## 📝 Requisitos

- **Python 3.9.x** (solo compatible con esta versión)
- **Node.js (v14 o superior)** (para el frontend Angular)
- **Cámara web conectada**
- **Cuenta en Backblaze B2** (para almacenamiento en la nube)
- **API Key de Gemini (Google Generative AI)**
- **Conexión a Internet**
- **Sistema operativo recomendado:** Windows 10/11 (probado en ambos)
- **Angular CLI** (`npm install -g @angular/cli`) linea de comandos de angular
- **(Opcional) ngrok** (si se requiere exponer servicios localmente)
- **MongoDB** (para la base de datos)
---

## 📦 Instalación

### 1️. Descarga el proyecto

Tienes dos opciones para obtener el código fuente:

- **Opción A: Clonar el repositorio con git**

  ```bat
  git clone https://github.com/javier020301001/AlarmaComunitaria.git
  ```
- **Opción B: Descargar el proyecto completo como archivo ZIP**

  Puedes descargar el proyecto completo como un archivo ZIP o cada archivo por separado.

Descomprime el ZIP o navega a la carpeta clonada según la opción que elegiste.

---

### 2️. (Opcional) Crea y activa un entorno virtual

```bat
py -3.9 -m venv venv
venv\Scripts\activate
```

---

### 3️. Instala las dependencias del backend (Python)

Primero, navega a la carpeta del backend de Python (cámara y sonido):

```bat
cd alarmaComunitaria/backend
pip install -r requirements.txt
```

Esto instalará todo lo necesario para la cámara y el servidor de sonido.

---

### 4️. Instala las dependencias del backend API (Node.js)

Navega a la carpeta del backend de la API:

```bat
cd alarmaComunitaria/backend/api
npm install
```

Esto instalará todas las dependencias necesarias para el backend Node.js (API REST y WebSocket).

---

### 5️. Instala las dependencias del frontend

Navega a la carpeta del frontend:

```bat
cd alarmaComunitaria/frontend
npm install
```

Esto instalará todas las dependencias necesarias para la interfaz web Angular.

---

### 6.Configura las credenciales

- **Backblaze B2:**  
  Edita las variables de credenciales en `camara.py` (o usa variables de entorno para mayor seguridad).
- **Gemini API Key:**  
  Edita la clave en `descripcionvideo.py` (o usa variables de entorno).

---

## 🚀 Uso

### 1️. Inicia el backend (notificaciones y API)

```bash
cd alarmaComunitaria/backend/api
node simple-server.js
```

### 2️. Inicia el servidor de sonido

```bash
cd alarmaComunitaria/backend/sonido
python servidorsonido.py
```

### 3️. Inicia el servidor de la cámara

```bash
cd alarmaComunitaria/backend/camara
python servidorcamara.py
```

### 4️. Inicia el frontend (interfaz web)

```bash
cd alarmaComunitaria/frontend  
ng serve
```

---

### 5️. Accede a la interfaz web

Abre tu navegador y ve a:  
```
http://localhost:4200
```

### 6️. Accede a la cámara
```
http://localhost:5001
```

---

### 7️. Prueba el sistema: alertas automáticas y manuales

- **Alerta automática:**  
  Realiza un movimiento sospechoso frente a la cámara (por ejemplo, muestra un cuchillo y mantenlo visible). El sistema grabará un video de 10 segundos, lo subirá a la nube y analizará la situación con IA. Recibirás una notificación en la interfaz web si se detecta una situación de inseguridad.

- **Alerta manual:**  
  Desde la interfaz web, puedes generar alertas manuales utilizando el formulario de notificación. Esto permite simular situaciones de emergencia y probar el sistema sin depender de la detección automática por cámara.

- **Activación de la sirena:**  
  Al presionar el botón de pánico en la web, se activa la sirena (alarma sonora) en el teléfono configurado como dispositivo de simulación.

---

## 🎯 Características Principales

- **Detección automática de armas y personas** usando modelos YOLOv8.
- **Grabación de video** solo cuando se detecta peligro, como: cercanía de dos personas, presencia de más de dos personas o detección de armas (10 segundos por evento).
- **Subida automática de videos** a Backblaze B2, con acceso mediante URL (registrada en `ultima_url.txt`).
- **Análisis de video con IA (Gemini):** Se genera una descripción textual y se filtran falsos positivos.
- **Notificaciones en tiempo real** a todos los usuarios conectados.
- **Interfaz web** para monitoreo, visualización de alertas y control de la sirena.
- **Alertas manuales** y botón para activar la alarma sonora.
- **Geolocalización de cámaras** (en desarrollo, requiere maduración).
- **Control de falsas alarmas** mediante análisis de la descripción generada por IA.

---

## 📂 Estructura del Proyecto

```text
AlarmaComunitaria-main/
│
├── alarmaComunitaria/                # Proyecto principal
│   ├── backend/                      # Backend: API, cámara y sonido
│   │   ├── api/                      # API REST y WebSocket (Node.js + Express)
│   │   │   ├── config/               # Configuración de la base de datos
│   │   │   ├── controllers/          # Controladores de rutas
│   │   │   ├── models/               # Modelos de datos (Mongoose)
│   │   │   ├── routes/               # Definición de rutas Express
│   │   │   ├── simple-server.js      # Servidor principal Node.js
│   │   │   ├── websocket-server.js   # Servidor WebSocket
│   │   │   └── ...                   # Otros archivos de configuración
│   │   │
│   │   ├── camara/                   # Lógica de cámara y detección (Python)
│   │   │   ├── camara.py             # Lógica principal de detección
│   │   │   ├── descripcionvideo.py   # Análisis de video con IA
│   │   │   ├── modelos/              # Modelos de IA (YOLO, BLIP, etc.)
│   │   │   │   ├── detect/           # Modelos de detección entrenados
│   │   │   │   │   ├── Db/           # Modelo alternativo
│   │   │   │   │   └── Normal_Compressed/ # Modelo principal
│   │   │   │   ├── yolov8n.pt        # Modelo YOLOv8 para personas
│   │   │   │   └── ...               # Otros modelos y recursos
│   │   │   ├── ngrok_url_camara.py   # Utilidad para exponer cámara con ngrok
│   │   │   ├── servidorcamara.py     # Servidor Flask para el stream de cámara
│   │   │   └── ...                   # Otros scripts auxiliares
│   │   │
│   │   ├── sonido/                   # Servidor de sonido/alarma (Python)
│   │   │   └── servidorsonido.py     # Activa la alarma en dispositivos
│   │   └── requirements.txt          # Dependencias Python
│   │
│   └──frontend/                     # Frontend: Angular
│       ├── src/
│       │   ├── app/
│       │   │   ├── Components/       # Componentes principales de la UI
│       │   │   │   ├── Inicio/       # Dashboard principal
│       │   │   │   ├── mapa/         # Mapa interactivo
│       │   │   │   ├── alertas/      # Listado de alertas
│       │   │   │   ├── alert-popup/  # Popup de alertas
│       │   │   │   ├── notification-button/ # Botón para enviar alertas
│       │   │   │   ├── notifications-panel/ # Panel de notificaciones
│       │   │   │   └── ...           # Otros componentes
│       │   │   ├── auth/             # Autenticación (login, registro, guards)
│       │   │   ├── services/         # Servicios Angular (API, WebSocket, etc.)
│       │   │   ├── Share/            # Interfaces y validadores compartidos
│       │   │   └── ...               # Configuración y archivos raíz
│       │   ├── assets/               # Imágenes y recursos estáticos
│       │   └── styles.scss           # Estilos globales
│       ├── angular.json              # Configuración Angular
│       ├── package.json              # Dependencias frontend
│       └── ...                       # Otros archivos de configuración
│   
├── README.md                         # Documentación principal
├── README_android.md                 # Instrucciones para Android
└── ultima_url.txt                    # Última URL de video subido
```

**Notas:**
- El backend y frontend están separados claramente para facilitar el desarrollo y despliegue.
- Los modelos de IA y scripts de cámara están en Python, mientras que la API y la interfaz web usan Node.js y Angular respectivamente.

---

## 🛠️ Personalizaciones

- Puedes cambiar los modelos YOLOv8 por otros entrenados (coloca los nuevos pesos en la carpeta de modelos).
- Ajusta la duración de grabación y umbrales de detección en `camara.py`.
- Mejora la interfaz web editando los componentes Angular en `frontend/src/app/`.
- Si deseas implementar una base de datos o almacenar datos extra, puedes hacerlo en la carpeta `backend/api` o crear un nuevo microservicio.

---

## 🔒 Seguridad

- **Credenciales:**  
  Las credenciales de Backblaze y la API Key de Gemini están en el código para pruebas.  
  **¡Cámbialas antes de usar en producción!**  
  Se recomienda usar variables de entorno para mayor seguridad.
- **Inicio de sesión:**  
  El sistema puede extenderse para autenticación de usuarios y cifrado de datos.

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

---

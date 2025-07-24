
# 📱 Complemento Extra: Sirena/Alarma en Teléfono Android

---

## 🛠️ Instalación y Configuración

1. **Instala Pydroid 3** desde Google Play.
2. **Abre Pydroid 3** y accede a la terminal (menú de tres líneas → Terminal).
3. **Instala las dependencias necesarias:**
   ```bash
   pip install flask
   pip install pygame
   ```

---

4. **Coloca el código** en la aplicación móvil, para esto se presentan estas dos alternativas.

## ✅ Alternativa 1: Código Manual

Copia y pega el siguiente código en Pydroid 3 y guárdalo como `servidorsirena.py`:

```python
# Sirena/Alarma para Android usando Flask y Pygame
from flask import Flask
from threading import Thread
import pygame

app = Flask(__name__)

# Inicializar solo el mixer, no todo pygame
pygame.mixer.init()

def play_sound():
    pygame.mixer.music.load('/storage/emulated/0/Download/sirena.mp3')
    pygame.mixer.music.play()

@app.route('/sonar', methods=['GET', 'POST'])
def sonar():
    print("Alerta recibida: Sonando alarma")
    Thread(target=play_sound).start()
    return "Alarma sonando", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005)
```

> **Importante:** El archivo `sirena.mp3` debe ser descargado por separado por medio del enlace.

---

## ✅ Alternativa 2: Código y archivo listos para usar

Puedes descargar el código fuente y el archivo de sonido desde el siguiente enlace:

**[Drive – Código y Sirena](https://drive.google.com/drive/folders/1Zw-_4UKkwG26lLyre9cQQca4_NYNh5BZ?usp=drive_link)**

---

5. **Obtén la dirección IP** local del teléfono Android.
6. **Colócala en el `servidorsonido.py`** del sistema principal.
7. **Ejecuta el script desde Pydroid.**

---

## ⚠️ Notas importantes

- El puerto en el script (`5005`) debe coincidir con el que se usa en la solicitud desde el sistema.
- El archivo `sirena.mp3` debe estar en una ruta accesible desde Pydroid.
- Ambos dispositivos deben estar conectados a la misma red Wi-Fi.
- Algunos teléfonos requieren habilitar permisos para ejecución en segundo plano o conexiones entrantes.

---

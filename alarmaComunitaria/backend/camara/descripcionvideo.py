import os
import cv2
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
import google.generativeai as genai
import requests 

# Ruta donde guardar los videos
VIDEO_DIR = "videos"
os.makedirs(VIDEO_DIR, exist_ok=True)

def obtener_url_desde_archivo(ruta_archivo="ultima_url.txt"):
    with open(ruta_archivo, "r") as f:
        url = f.read().strip()
    return url

def descargar_video(url, destino=None):
    if destino is None:
        nombre = os.path.basename(url.split("?")[0])
        destino = os.path.join(VIDEO_DIR, nombre)
    r = requests.get(url, stream=True)
    with open(destino, 'wb') as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    return destino

FPS_TARGET = 1.0
print("Cargando modelo BLIP (Salesforce/blip-image-captioning-large).")
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large").to("cpu")

def extract_frames(path: str, fps_target: float):
    cap = cv2.VideoCapture(path)
    real_fps = cap.get(cv2.CAP_PROP_FPS) or 30
    step = max(int(real_fps / fps_target), 1)

    count = 0
    frames = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if count % step == 0:
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            frames.append(img)
        count += 1

    cap.release()
    print(f"Extraídos {len(frames)} fotogramas…")
    return frames

def caption_image(img):
    inputs = processor(images=img, return_tensors="pt").to("cpu")
    out = model.generate(**inputs, max_new_tokens=60)
    return processor.decode(out[0], skip_special_tokens=True)

def caption_video(path: str, fps_target: float):
    frames = extract_frames(path, fps_target)
    captions = [caption_image(f) for f in frames]
    return captions

def main():
    url_video = obtener_url_desde_archivo()
    ruta_local = descargar_video(url_video)

    captions = caption_video(ruta_local, FPS_TARGET)
    texto = "\n".join(captions)
    print(texto)

    # borra el video local después de analizar
    if os.path.exists(ruta_local):
        os.remove(ruta_local)


    return texto

def Answer(descripcion_limpia):
    #genai.configure(api_key="AIzaSyB30ATaQjJ9WXDwpCWUBaQHmNeMSUjBymQ")
    genai.configure(api_key="AIzaSyC5Syb7buqY9WKV5tMNKavPZqyS8DAWY_8")

    prompt = (
    "El siguiente texto contiene varias frases que describen escenas de un video.\n\n"
    "Tu tarea es analizar las frases en orden y buscar el primer indicio de inseguridad, peligro o delito. "
    "En particular, pon atención a lo siguiente:\n"
    "- Si una persona sostiene, porta o muestra una pistola, cuchillo, arma de fuego, arma blanca u objeto amenazante.\n"
    "- Si hay peleas, agresiones físicas o verbales, empujones, gritos, comportamientos violentos o amenazantes.\n"
    "- Si hay un asalto, intento de robo, secuestro, amenaza o situación de peligro evidente.\n\n"
    "Tu respuesta debe describir sólo el PRIMER hecho peligroso que detectes, en español, con una frase clara y breve.\n"
    "Ignora hechos posteriores aunque sean diferentes o repetidos.\n\n"
    "Si NO hay ninguna frase que indique inseguridad, peligro o delito, responde exactamente:\n"
    "Seguridad\n\n"
    "En caso de que detectes inseguridad, la respuesta debe empezar con:\n"
    "Inseguridad seguido de la descripción del primer suceso encontrado.\n\n"
    "Ejemplos:\n\n"
    "Texto:\n"
    "a man is holding a knife\n"
    "a man is holding a gun\n"
    "Respuesta:\n"
    "Inseguridad\nUn hombre sostiene un cuchillo.\n\n"
    "Texto:\n"
    "a woman is yelling at another woman\n"
    "a man is holding a gun\n"
    "Respuesta:\n"
    "Inseguridad\nUna mujer le grita a otra mujer.\n\n"
    "Texto:\n"
    "a boy is playing with a toy\n"
    "a boy is painting\n"
    "Respuesta:\n"
    "Seguridad\n\n"
    "### Ahora analiza este texto:" )



    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(f"{prompt} El siguiente texto: {descripcion_limpia}")
    print("Proceso de descripción completa.")
    return response.text

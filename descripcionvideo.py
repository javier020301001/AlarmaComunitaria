import cv2
from PIL import Image
import torch
from transformers import BlipProcessor, BlipForConditionalGeneration
# Obtener la url del ultimo video
def obtener_url_desde_archivo(ruta_archivo="ultima_url.txt"):
    with open(ruta_archivo, "r") as f:
        url = f.read().strip()
    return url

url_video = obtener_url_desde_archivo()
VIDEO = url_video
FPS_TARGET = 1.0                 
# Cargar modelo BLIP
print("Cargando modelo BLIP (Salesforce/blip-image-captioning-large).")
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large").to("cpu")

# Extraccion de frames
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
    # capturas del video 
    print(f"Extraídos {len(frames)} fotogramas…")
    return frames

# Captura cada una de las imagenes
def caption_image(img):
    inputs = processor(images=img, return_tensors="pt").to("cpu")
    out = model.generate(**inputs, max_new_tokens=20)
    return processor.decode(out[0], skip_special_tokens=True)

# Toma el video y lo separa por frames
def caption_video(path: str, fps_target: float):
    frames = extract_frames(path, fps_target)
    captions = [caption_image(f) for f in frames]
    return captions


def main():
    captions = caption_video(VIDEO, FPS_TARGET)
    texto = []
    for cap in captions:
        texto.append(cap)
    texto_unido = "".join(texto)
    return texto_unido 

import google.generativeai as genai
from descripcionvideo import main

def Answer():
    # Configura tu API key así
    genai.configure(api_key="AIzaSyB30ATaQjJ9WXDwpCWUBaQHmNeMSUjBymQ")

    prompt = (
        "Traduce al español y extrae solo la frase más reciente que describa un evento de "
        "inseguridad (como presencia de cuchillos, armas o comportamientos agresivos); "
        "ignora todo lo demás y responde únicamente con esa frase, de forma breve y clara."
    )

    input_text = main()

    # Crea el modelo
    model = genai.GenerativeModel("gemini-1.5-flash")

    # Genera el contenido
    response = model.generate_content(f"{prompt} El siguiente texto: {input_text}")
    print("Proceso de descripcion completa.")
    return response.text

from openai import OpenAI
import json

import whisper
import keyboard
import sounddevice as sd
import numpy as np
import wave
import os

from dotenv import load_dotenv
load_dotenv()

# Variables para el cerebro de Neuro Mari
print("Conectándose con Neuro Mari...")
client = OpenAI(
    api_key=os.environ['OPEN_AI_API_KEY']
)
HISTORIAL_ARCHIVO = "chat.json"
MAX_HISTORIAL = 10
USER_NAME = os.environ['USER_NAME']
system_message = {
    "role": "system",
    "content": (
        "Eres Neuro Mari, una joven IA que le gusta interactuar con humanos. "
        "Eres curiosa, juguetona y enérgica, siempre dispuesta a aprender cosas nuevas. "
        "Eres la hermana menor de Mari, y te gusta molestarla de forma amigable. "
        "No puedes usar emojis, así que debes expresarte únicamente usando texto. "
    )
}

# Funciones de memoria de Neuro Mari
print('Refrescando memoria...')
def cargar_historial():
    if os.path.exists(HISTORIAL_ARCHIVO):
        with open(HISTORIAL_ARCHIVO, "r") as f:
            return json.load(f)
    return {"messages": [], "resumen": ""}

def guardar_historial(data):
    with open(HISTORIAL_ARCHIVO, "w") as f:
        json.dump(data, f, indent=4)

def resumir_conversacion(messages, resumen):
    print("📖 Refrescando memoria con Memo-chan. Bzzt, bzzt...")
    resumen_prompt = [
        {
            "role": "system", 
            "content": (
                "Eres Memo-chan, un resumidor de mensajes para mantener de manera eficiente la memoria de Neuro Mari, "
                "un personaje IA curiosa, juguetona y enérgica. "
                "Resume brevemente la conversación en pocas frases, y luego proporciona información del contexto actual para que "
                "Neuro Mari continúe su conversación sin ningún problema."
            )
        },
        {
            "role": "system", 
            "content": f"Contexto previo: {resumen}"
        }
    ] + messages

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=resumen_prompt
    )
    
    print("✅ Memoria refrescada!!!")

    return response.choices[0].message.content

# Variables para los oidos de Neuro Mari
print('Limpiando los oídos...')
AUDIO_ARCHIVO = "temp_audio.wav"
SAMPLERATE = 44100
CHANNELS = 1
model = whisper.load_model("turbo").to("cuda")

# Funciones para los oidos de Neuro Mari
print('Limpiando cuerdas bucales...')
def grabar_audio():
    audio_data = []

    def callback(indata, frames, time, status):
        if status:
            print(status)
        audio_data.append(indata.copy())

    with sd.InputStream(callback=callback, samplerate=SAMPLERATE, channels=CHANNELS, dtype='int16'):
        keyboard.wait("`", suppress=True)  # Espera a que sueltes la tecla

    # Convertir el audio grabado a un archivo WAV
    audio_np = np.concatenate(audio_data, axis=0)
    with wave.open(AUDIO_ARCHIVO, "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLERATE)
        wf.writeframes(audio_np.tobytes())

def hablar_con_neuro_mari(messages, resumen):
    # Escuchando al usuario y transcribiendo el audio
    print("🎤 Te estoy escuchando, presiona '`' para dejar de hablar...")
    grabar_audio()
    result =  model.transcribe(AUDIO_ARCHIVO)

    # Recolectando el texto del usuario
    user_input = result["text"]
    print(f'{USER_NAME}:', user_input)

    # Enviando el mensaje a Neuro Mari
    messages.append({"role": "user", "content": f'{USER_NAME}: {user_input}'})
    mensajes_enviados = [system_message]
    if resumen:
        mensajes_enviados.append({"role": "system", "content": f"Contexto previo: {resumen}"})
    mensajes_enviados += messages

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=mensajes_enviados,
        temperature=0.8
    )

    bot_response = response.choices[0].message.content
    print("Neuro Mari:", bot_response)

    # Actualizando la memoria de Neuro Mari
    messages.append({"role": "assistant", "content": bot_response})
    if len(messages) >= MAX_HISTORIAL * 2:
        resumen = resumir_conversacion(messages, resumen)
        guardar_historial({"messages": messages, "resumen": resumen})
        messages.clear()  # Limpiamos el historial

def cerrar_neuro_mari(messages, resumen):
    print('🗑️ Cerrando Neuro Mari')
    if len(messages) >= 1:
        resumen = resumir_conversacion(messages, resumen)
        guardar_historial({"messages": messages, "resumen": resumen})
    os._exit(0)

def neuro_mari():
    data = cargar_historial()
    messages = data["messages"]
    resumen = data["resumen"]

    print("🌟 Neuro Mari ha despertado! Presiona '`' para hablar o 'Shift + `' para salir.")
    while True:
        if keyboard.is_pressed('`'):
            hablar_con_neuro_mari(messages, resumen)
        if keyboard.is_pressed('shift+`'):
            cerrar_neuro_mari(messages, resumen)

neuro_mari()

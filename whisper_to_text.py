import whisper
import keyboard
import sounddevice as sd
import numpy as np
import wave
import os

AUDIO_ARCHIVO = "temp_audio.wav"

# 🔹 Configuración del micrófono
SAMPLERATE = 44100  # Frecuencia de muestreo
CHANNELS = 1  # Mono

print('Cargando el modelo en la GPU...')
# Usa GPU para acelerar (tiny, base, small, medium, large, turbo)
model = whisper.load_model("turbo").to("cuda")

# 🎙️ Función para grabar audio mientras se mantiene presionada la tecla
def grabar_audio():
    print("🎤 Grabando... (Habla mientras mantengas presionado '~')")

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

    print("✅ Audio guardado.")

# 📜 Función para transcribir el audio con Whisper local
def transcribir_audio():
    print("🔄 Transcribiendo...")
    result = model.transcribe(AUDIO_ARCHIVO)
    print("📝 Transcripción:", result["text"])

# 🔥 Función principal que combina ambas tareas
def escuchar_y_transcribir():
    grabar_audio()
    transcribir_audio()

# 🛠️ Configurar los comandos
keyboard.add_hotkey("`", escuchar_y_transcribir)  # Iniciar STT con '~'
keyboard.add_hotkey("shift+`", lambda: os._exit(0))  # Cerrar con 'Shift + ~'

print("🎤 Presiona '`' para hablar")
print("❌ Presiona 'Shift + `' para salir")

keyboard.wait()  # Mantiene el programa en ejecución

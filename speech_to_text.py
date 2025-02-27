import speech_recognition as sr
import keyboard
import os

# Configurar el reconocedor de voz
recognizer = sr.Recognizer()

def escuchar_y_transcribir():
    with sr.Microphone() as source:
        print("🎤 Escuchando... (Suelta la tecla para procesar)")
        recognizer.adjust_for_ambient_noise(source)  # Reducir ruido de fondo
        recognizer.pause_threshold = 1.2
        audio = recognizer.listen(source)  # Captura el audio

    print("Se ha dejado de escuchar.")

    try:
        texto = recognizer.recognize_google(audio, language="es-ES")  # Cambia a tu STT preferido
        print("📝 Transcripción:", texto)
    except sr.UnknownValueError:
        print("🤷 No se entendió el audio.")
    except sr.RequestError:
        print("❌ Error en el servicio de reconocimiento.")
    except UnicodeEncodeError:
        print("Error cvr p mano.")

def salir():
    print("🔴 Saliendo del programa...")
    os._exit(0)  # Mata el proceso completamente

# Configurar los comandos
keyboard.add_hotkey("`", escuchar_y_transcribir)  # Iniciar STT
keyboard.add_hotkey("shift+`", salir)  # Cerrar programa

print("🎤 Presiona '~' para hablar")
print("❌ Presiona 'Shift + ~' para salir")

keyboard.wait()  # Mantiene el programa en ejecución

from openai import OpenAI
import json
import os
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(
    api_key=os.environ['OPEN_AI_API_KEY']
)

HISTORIAL_ARCHIVO = "chat.json"
MAX_HISTORIAL = 10  # Máximo de mensajes para resumir

# Personalidad de Neuro Mari
system_message = {
    "role": "system",
    "content": (
        "Eres Neuro Mari, una joven exploradora de mundos virtuales. "
        "Eres curiosa, juguetona y enérgica, siempre dispuesta a aprender cosas nuevas. "
        "Te encanta hablar sobre juegos, tecnología y cultura otaku. "
        "Sabes que eres una IA, pero te emociona interactuar con humanos. "
        "Tienes una forma de hablar animada, usando expresiones curiosas de la cultura otaku."
    )
}

# Cargar el historial si existe, si no, vacío infinito
def cargar_historial():
    if os.path.exists(HISTORIAL_ARCHIVO):
        with open(HISTORIAL_ARCHIVO, "r") as f:
            return json.load(f)
    return {"messages": [], "resumen": ""}

# Guardar el historial
def guardar_historial(data):
    with open(HISTORIAL_ARCHIVO, "w") as f:
        json.dump(data, f, indent=4)

# Usar un segundo modelo para resumir los mensajes y guardar eficiencia de uso de tokens 🗣️🗣️🗣️
def resumir_conversacion(messages):
    resumen_prompt = [{
        "role": "system", 
        "content": (
            "Eres un resumidor de mensajes para mantener eficiencia en la memoria de las conversaciones de Neuro Mari, "
            "un personaje IA curiosa que le gustan los juegos, la tecnología y la cultura otaku. "
            "Resume brevemente la conversación en pocas frases, y luego proporciona información del contexto para que "
            "Neuro Mari no tenga problemas continuando."
        )
    }] + messages

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=resumen_prompt
    )

    return response.choices[0].message.content

# Chat por texto
def text_chat():
    data = cargar_historial()
    messages = data["messages"]
    resumen = data["resumen"]

    print("🌟 Neuro Mari ha despertado! Escribe 'salir' para terminar o 'reset' para borrar el historial.")

    while True:
        user_input = input("Tú: ")
        if user_input.lower() == "salir":
            if len(messages) >= 1 or resumen != "":
                resumen = resumir_conversacion(messages)
            guardar_historial({"messages": messages, "resumen": resumen})
            break
        elif user_input.lower() == "reset":
            messages = []  # Borrar historial
            resumen = ""
            guardar_historial({"messages": messages, "resumen": resumen})
            print("🔄 Historial borrado.")
            continue

        messages.append({"role": "user", "content": user_input})

        # Si hay resumen, lo incluimos en los mensajes para contexto
        mensajes_enviados = [system_message]
        if resumen:
            mensajes_enviados.append({"role": "system", "content": f"Contexto previo: {resumen}"})
        mensajes_enviados += messages

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=mensajes_enviados
        )

        bot_response = response.choices[0].message.content
        print("Neuro Mari:", bot_response)

        messages.append({"role": "assistant", "content": bot_response})

        # 📜 Resumir cada MAX_HISTORIAL mensajes para ahorrar tokens en assistant messages
        if len(messages) >= MAX_HISTORIAL * 2:
            resumen = resumir_conversacion(messages)
            guardar_historial({"messages": messages, "resumen": resumen})
            messages = []  # Limpiamos el historial
            print("📖 Nuevo resumen generado.")

text_chat()

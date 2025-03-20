from flask import Flask, request, jsonify
import requests
import openai
from dotenv import load_dotenv
import os

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

# Endpoint que usa la API BOE y luego GPT para responder
@app.route('/preguntar', methods=['POST'])
def preguntar():
    data = request.json
    pregunta_usuario = data.get("pregunta")
    fecha = data.get("fecha") # AAAAMMDD

    # Consultar la API del BOE
    boe_respuesta = requests.get(f'https://boe.es/datosabiertos/api/boe/sumario/{fecha}', headers={"Accept":"application/json"})
    
    if boe_respuesta.status_code != 200:
        return jsonify({"error": "No hay datos para esa fecha"}), 404

    datos_boe = boe_respuesta.json()

    # Usar GPT para generar una respuesta útil con los datos obtenidos
    prompt = f"Teniendo estos datos del BOE: {datos_boe['data']['sumario'][:5]} responde brevemente esta pregunta: {pregunta_usuario}"

    respuesta_gpt = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )

    return jsonify({"respuesta": respuesta_gpt.choices[0].message.content})

if __name__ == '__main__':
    app.run(debug=True)

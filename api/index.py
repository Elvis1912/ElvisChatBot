import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq

app = Flask(__name__)
# Habilitar CORS para permitir peticiones desde el frontend (violoncello.html)
CORS(app)

# Inicializar cliente de Groq
# La API key se tomará automáticamente de la variable de entorno GROQ_API_KEY en Vercel
client = Groq()

# Leer la información de la página al iniciar el servidor (Serverless approach)
try:
    # Usar ruta absoluta basada en la ubicación de este archivo index.py
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, 'InformacionDeLaPagina.txt')
    
    with open(file_path, 'r', encoding='utf-8') as f:
        PAGE_INFO = f.read()
except FileNotFoundError:
    print(f"Error: No se encontró el archivo 'InformacionDeLaPagina.txt' en la ruta {file_path}")
    PAGE_INFO = ""

@app.route('/api/chat', methods=['POST', 'OPTIONS'])
@app.route('/chat', methods=['POST', 'OPTIONS'])
def chat():
    # Obtener el mensaje del usuario desde el cuerpo de la petición
    data = request.json
    user_message = data.get('message', '')

    if not user_message:
        return jsonify({'error': 'El mensaje no puede estar vacío'}), 400

    try:
        # Construir los mensajes para el modelo
        messages = [
            {
                "role": "system",
                "content": (
                    "Eres un asistente virtual experto en el violoncello para una página web educativa. "
                    "Responde a las preguntas de los usuarios basándote ÚNICAMENTE en la siguiente información:\n\n"
                    f"{PAGE_INFO}\n\n"
                    "Si el usuario hace una pregunta que no se puede responder con esta información, dile de forma educada que no tienes "
                    "información sobre ese tema y sugiere que te pregunten sobre la historia, características, técnicas o chelistas famosos mencionados en la página. "
                    "Sé conciso, amigable y mantén las respuestas relativamente cortas para un formato de chat."
                )
            },
            {
                "role": "user",
                "content": user_message
            }
        ]

        # Realizar la petición a la API de Groq
        chat_completion = client.chat.completions.create(
            messages=messages,
            model="llama-3.1-8b-instant", # Se puede cambiar por otro modelo si es necesario, como llama3-70b-8192 o mixtral-8x7b-32768
            temperature=0.7,
            max_tokens=500,
        )

        bot_reply = chat_completion.choices[0].message.content

        return jsonify({'reply': bot_reply})

    except Exception as e:
        print(f"Error al conectar con Groq: {str(e)}")
        return jsonify({'error': 'Hubo un error al procesar tu solicitud.'}), 500

if __name__ == '__main__':
    # Se ejecuta en el puerto 5000 por defecto
    app.run(debug=True, port=5000)

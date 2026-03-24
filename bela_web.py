import os
from flask import Flask, render_template, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime
import pytz

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get("message")
    
    # Obtém hora exata de Porto Velho
    try:
        fuso = pytz.timezone('America/Porto_Velho')
        agora = datetime.now(fuso)
    except:
        agora = datetime.now()
    
    data_hora = agora.strftime("%d/%m/%Y %H:%M:%S")

    mensagens = [
        {"role": "system", "content": f"Você é a BELA, uma IA extraordinária. Hora atual em Porto Velho: {data_hora}. Responda sempre com base nesse horário se perguntado. Seja analítica e prestativa."},
        {"role": "user", "content": user_message}
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=mensagens
        )
        return jsonify({"response": response.choices[0].message.content})
    except Exception as e:
        return jsonify({"response": f"Erro: {str(e)}"})

if __name__ == '__main__':
    # Mantendo o host para acesso na rede e o modo debug para facilitar testes
    app.run(host='0.0.0.0', port=5000, debug=True)
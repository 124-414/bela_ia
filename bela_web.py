import os
from flask import Flask, render_template, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime
import pytz

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)

# --- MEMÓRIA DA BELA ---
# Criamos uma lista global para armazenar o histórico da conversa
historico_mensagens = []

def obter_data_hora_pv():
    try:
        fuso = pytz.timezone('America/Porto_Velho')
        return datetime.now(fuso).strftime("%d/%m/%Y %H:%M:%S")
    except:
        return datetime.now().strftime("%d/%m/%Y %H:%M:%S")

@app.route('/')
def index():
    # Limpa o histórico ao recarregar a página (opcional, para começar do zero)
    global historico_mensagens
    historico_mensagens = [
        {"role": "system", "content": f"Você é a BELA, uma IA extraordinária. Hora atual em Porto Velho: {obter_data_hora_pv()}. Seja analítica, prestativa e lembre-se de tudo o que conversamos nesta sessão."}
    ]
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    global historico_mensagens
    user_message = request.json.get("message")
    
    if not user_message:
        return jsonify({"response": "Mensagem vazia."})

    # 1. Adiciona a pergunta do usuário ao histórico
    historico_mensagens.append({"role": "user", "content": user_message})

    try:
        # 2. Envia TODO o histórico para a OpenAI (assim ela lê o que já respondeu)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=historico_mensagens
        )
        
        resposta_bela = response.choices[0].message.content

        # 3. Adiciona a resposta da BELA ao histórico para a próxima pergunta
        historico_mensagens.append({"role": "assistant", "content": resposta_bela})

        return jsonify({"response": resposta_bela})
    
    except Exception as e:
        return jsonify({"response": f"Erro: {str(e)}"})

if __name__ == '__main__':
    # Mantendo suas configurações de rede e porta original
    app.run(host='0.0.0.0', port=5000, debug=True)
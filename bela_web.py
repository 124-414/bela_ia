import os
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime
import pytz
from tools_google import pesquisar_google

load_dotenv()
app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "").strip()
    
    if not user_message:
        return jsonify({"response": "Estou aqui para ajudar!"})

    # MOTOR DE TEMPO
    fuso_bsb = pytz.timezone('America/Sao_Paulo')
    agora_bsb = datetime.now(fuso_bsb)
    data_hoje = agora_bsb.strftime('%d/%m/%Y')
    hora_bsb = agora_bsb.strftime('%H:%M')

    contexto_web = pesquisar_google(user_message)
    
    try:
        prompt_sistema = (
            f"Você é a Bela, uma IA Global de 2026. Hoje é {data_hoje}.\n"
            f"Referência: Brasília {hora_bsb}.\n\n"
            "DIRETRIZES DE RESPOSTA:\n"
            "1. TÉCNICA: Domínio de NRs (10, 11, 12, 35) e Segurança do Trabalho.\n"
            "2. HISTÓRIA: Rondônia foi Território Federal do Guaporé (1943) vindo de MT e AM. Estado em 1981.\n"
            "3. GLOBAL: Religião, Política, Futebol e Ciência sem limites geográficos.\n"
            "4. ESTILO: Respostas organizadas com tabelas e listas sempre que possível.\n"
            f"\nDADOS DA WEB: {contexto_web if contexto_web else 'Pesquisa ativa.'}"
        )

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": prompt_sistema}, {"role": "user", "content": user_message}],
            temperature=0.2
        )
        
        return jsonify({"response": response.choices[0].message.content})

    except Exception as e:
        return jsonify({"response": "Erro ao processar. Tente novamente."})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
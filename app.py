import os
from datetime import datetime
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from openai import OpenAI

# Carrega variáveis do .env (opcional em produção)
load_dotenv()

app = Flask(__name__)

# Configura cliente OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/")
def home():
    return "🚀 IA online e funcionando!"

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        user_message = data.get("message")

        # 📅 Envia data atual para evitar erro de 2023
        data_atual = datetime.now().strftime("%d/%m/%Y")

        resposta = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"Hoje é {data_atual}. Responda considerando a data atual."},
                {"role": "user", "content": user_message}
            ]
        )

        return jsonify({
            "response": resposta.choices[0].message.content
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 🔥 IMPORTANTE PARA RENDER
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
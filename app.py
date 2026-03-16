import os
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from openai import OpenAI

# Carrega variáveis do .env
load_dotenv()

app = Flask(__name__)

# Cliente OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Página principal
@app.route("/")
def home():
    return render_template("index.html")

# API do chat
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        user_message = data.get("message")

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


# Rodar servidor
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
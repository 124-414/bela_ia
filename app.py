import os
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

app = Flask(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# memória simples da conversa
memoria = []

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():

    data = request.json
    user_message = data.get("message")

    data_atual = datetime.now().strftime("%d/%m/%Y")
    hora_atual = datetime.now().strftime("%H:%M")

    memoria.append({
        "role": "user",
        "content": user_message
    })

    resposta = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": f"""
Você é a Bela IA.

Hoje é {data_atual}
A hora atual é {hora_atual}

Responda em português.
Se perguntarem hora ou data use essas informações.
"""
            }
        ] + memoria
    )

    reply = resposta.choices[0].message.content

    memoria.append({
        "role": "assistant",
        "content": reply
    })

    return jsonify({"response": reply})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
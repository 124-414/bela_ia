import os
from flask import Flask, request, jsonify, render_template
from openai import OpenAI
from config import OPENAI_API_KEY
from router import executar_tools

app = Flask(__name__)

client = OpenAI(api_key=OPENAI_API_KEY)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")

    # 🔥 Executa ferramentas automaticamente
    contexto_tools = executar_tools(user_message)

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Você é uma IA estilo GPT com acesso a ferramentas."
                },
                {
                    "role": "user",
                    "content": contexto_tools + "\nPergunta: " + user_message
                }
            ]
        )

        answer = response.choices[0].message.content

    except Exception as e:
        answer = "Erro ao gerar resposta."

    return jsonify({"response": answer})


if __name__ == "__main__":
    app.run(debug=True)
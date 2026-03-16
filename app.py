import os
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from openai import OpenAI
from dotenv import load_dotenv

from database import init_db, save, history
from tools_google import google_search
from tools_pdf import read_pdf
from tools_image import create_image

load_dotenv()

app = Flask(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

init_db()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():

    try:

        msg = request.json.get("message", "").strip()

        if not msg:
            return jsonify({"response": "Digite uma mensagem."})

        save("user", msg)

        # Data e hora real do servidor
        agora = datetime.now().strftime("%d/%m/%Y %H:%M")

        system_prompt = f"""
Hoje é {agora}.
Responda de forma clara e objetiva.
"""

        # IMAGEM
        if msg.startswith("imagem:"):
            prompt = msg.replace("imagem:", "").strip()
            url = create_image(prompt)
            reply = f"<img src='{url}' width='300'>"
            save("assistant", reply)
            return jsonify({"response": reply})

        # GOOGLE
        if msg.startswith("google:"):
            query = msg.replace("google:", "").strip()
            result = google_search(query)
            msg = f"Resultados da pesquisa:\n{result}"

        # MEMÓRIA
        hist = history()

        response = client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {"role": "system", "content": system_prompt},
                *hist,
                {"role": "user", "content": msg}
            ]
        )

        reply = response.output_text

        save("assistant", reply)

        return jsonify({"response": reply})

    except Exception as e:
        print("Erro:", e)
        return jsonify({"response": "Erro interno no servidor."})


@app.route("/upload", methods=["POST"])
def upload():

    try:
        file = request.files.get("file")
        if not file:
            return jsonify({"text": "Nenhum arquivo enviado."})

        text = read_pdf(file)
        return jsonify({"text": text})

    except Exception as e:
        print("Erro upload:", e)
        return jsonify({"text": "Erro ao ler arquivo."})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
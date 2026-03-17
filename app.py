import os
import re
import threading
from datetime import datetime

import pytz
from flask import Flask, request, jsonify, render_template
from openai import OpenAI
from dotenv import load_dotenv

from database import init_db, save, history
from tools_google import google_search
from tools_pdf import read_pdf
from tools_image import create_image
from tools_news import buscar_noticias

load_dotenv()

app = Flask(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

init_db()

brasil = pytz.timezone("America/Sao_Paulo")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json()

    if not data or "message" not in data:
        return jsonify({"response": "Mensagem inválida."})

    msg_original = data["message"]
    save("user", msg_original)

    texto = msg_original.lower()
    msg_final = msg_original

    # ⏰ HORA
    if "que horas" in texto or texto.strip() == "hora":
        agora = datetime.now(brasil).strftime("%H:%M:%S")
        reply = f"Agora são {agora}."
        save("assistant", reply)
        return jsonify({"response": reply})

    # 📅 DATA
    if "que dia" in texto or "data" in texto or texto.strip() == "hoje":
        hoje = datetime.now(brasil).strftime("%d/%m/%Y")
        reply = f"Hoje é {hoje}."
        save("assistant", reply)
        return jsonify({"response": reply})

    # 🖼 IMAGEM
    if msg_original.startswith("imagem:") or "criar imagem" in texto:
        prompt = msg_original.replace("imagem:", "").strip()

        try:
            url = create_image(prompt)
            reply = f"<img src='{url}' width='300'>"
        except Exception as e:
            reply = f"Erro ao gerar imagem: {str(e)}"

        save("assistant", reply)
        return jsonify({"response": reply})

    # 🌍 BUSCA PROFISSIONAL (NEWS API + FALLBACK)

    res = ""

    # 🔥 1. tenta NewsAPI
    try:
        res = buscar_noticias(msg_original)
    except Exception as e:
        print("Erro NewsAPI:", e)

    # 🔥 2. fallback Google com timeout
    if not res:
        def busca():
            global res
            try:
                res = google_search(msg_original)
            except:
                res = ""

        t = threading.Thread(target=busca)
        t.start()
        t.join(timeout=3)

    # 🧠 monta prompt com contexto real
    if res and len(res.strip()) > 50:
        msg_final = f"""
Use SOMENTE as informações abaixo para responder:

{res}

Pergunta:
{msg_original}
"""

    hist = history()[-5:]

    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            timeout=10,
            input=[
                {
                    "role": "system",
                    "content": """
Você é uma IA atualizada com acesso a notícias reais da internet.

Regras:
- Seja direto e claro
- Se houver notícias, resuma os fatos
- Nunca diga que não tem acesso à internet
"""
                }
            ] + hist + [
                {"role": "user", "content": msg_final}
            ]
        )

        reply = response.output_text

        # limpa caracteres estranhos
        reply = re.sub(r'[\*_`]', '', reply)

    except Exception as e:
        reply = f"Erro na IA: {str(e)}"

    save("assistant", reply)

    return jsonify({"response": reply})


@app.route("/upload", methods=["POST"])
def upload():

    if "file" not in request.files:
        return jsonify({"text": "Nenhum arquivo enviado."})

    file = request.files["file"]
    text = read_pdf(file)

    return jsonify({"text": text})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
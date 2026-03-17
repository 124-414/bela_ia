import os
import re
from datetime import datetime
import pytz
from flask import Flask, request, jsonify, render_template
from openai import OpenAI
from dotenv import load_dotenv

from database import init_db, save, history
from tools_google import google_search
from tools_pdf import read_pdf
from tools_image import create_image

load_dotenv()

app = Flask(__name__)

# 🔑 OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 📦 Banco de dados
init_db()

# 🌎 Fuso horário Brasil
brasil = pytz.timezone("America/Sao_Paulo")


# 🏠 Página inicial
@app.route("/")
def home():
    return render_template("index.html")


# 💬 CHAT
@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json()

    if not data or "message" not in data:
        return jsonify({"response": "Mensagem inválida."})

    msg_original = data["message"]
    save("user", msg_original)

    texto = msg_original.lower()
    msg_final = msg_original

    # ⏰ HORA (PRIORIDADE TOTAL)
    if "que horas" in texto or texto.strip() == "hora":
        agora = datetime.now(brasil).strftime("%H:%M:%S")
        reply = f"Agora são {agora}."
        save("assistant", reply)
        return jsonify({"response": reply})

    # 📅 DATA (PRIORIDADE TOTAL)
    if "que dia" in texto or "data" in texto or texto.strip() == "hoje":
        hoje = datetime.now(brasil).strftime("%d/%m/%Y")
        reply = f"Hoje é {hoje}."
        save("assistant", reply)
        return jsonify({"response": reply})

    # 🖼 IMAGEM
    if msg_original.startswith("imagem:") or "criar imagem" in texto or "gerar imagem" in texto:
        if msg_original.startswith("imagem:"):
            prompt = msg_original.replace("imagem:", "").strip()
        else:
            prompt = msg_original

        try:
            url = create_image(prompt)
            reply = f"<img src='{url}' width='300'>"
        except Exception as e:
            reply = f"Erro ao gerar imagem: {str(e)}"

        save("assistant", reply)
        return jsonify({"response": reply})

    # 🌍 BUSCA NA INTERNET
    try:
        res = google_search(msg_original)

        if res and res.strip() != "":
            msg_final = f"""
Use as informações atualizadas da internet abaixo para responder.

Dados da web:
{res}

Pergunta:
{msg_original}
"""
    except Exception as e:
        print("Erro na busca:", e)

    # 🧠 HISTÓRICO (LIMITADO)
    hist = history()[-5:]

    # 🚫 BLOQUEIO ANTI-CONFLITO (DATA/HORA)
    if any(p in texto for p in ["data", "dia", "hoje", "horas", "hora"]):
        hist = []

    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {
                    "role": "system",
                    "content": "Responda sempre em texto simples, direto e atualizado. Nunca invente datas ou horários. Use informações da internet quando disponíveis."
                }
            ] + hist + [
                {"role": "user", "content": msg_final}
            ]
        )

        reply = response.output_text

        # 🔥 Limpeza de formatação
        reply = re.sub(r'[\*_`]', '', reply)

    except Exception as e:
        reply = f"Erro na IA: {str(e)}"

    save("assistant", reply)

    return jsonify({"response": reply})


# 📂 UPLOAD PDF
@app.route("/upload", methods=["POST"])
def upload():

    if "file" not in request.files:
        return jsonify({"text": "Nenhum arquivo enviado."})

    file = request.files["file"]
    text = read_pdf(file)

    return jsonify({"text": text})


# 🚀 EXECUÇÃO LOCAL / RENDER
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
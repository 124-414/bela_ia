import os
import re
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

# 🔑 OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 📦 Banco
init_db()


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

    msg = data["message"]
    save("user", msg)

    texto = msg.lower()

    # ⏰ HORA
    if "que horas" in texto or "hora" == texto.strip():
        agora = datetime.now().strftime("%H:%M:%S")
        reply = f"Agora são {agora}."
        save("assistant", reply)
        return jsonify({"response": reply})

    # 📅 DATA
    if "que dia" in texto or "hoje" in texto:
        hoje = datetime.now().strftime("%d/%m/%Y")
        reply = f"Hoje é {hoje}."
        save("assistant", reply)
        return jsonify({"response": reply})

    # 🖼 IMAGEM
    if msg.startswith("imagem:") or "criar imagem" in texto or "gerar imagem" in texto:
        if msg.startswith("imagem:"):
            prompt = msg.replace("imagem:", "").strip()
        else:
            prompt = msg
        try:
            url = create_image(prompt)
            reply = f"<img src='{url}' width='300'>"
        except Exception as e:
            reply = f"Erro ao gerar imagem: {str(e)}"
        save("assistant", reply)
        return jsonify({"response": reply})

    # 🌍 BUSCA AUTOMÁTICA INTELIGENTE
    try:
        res = google_search(msg)
        if res:
            msg = f"""
Use as informações atualizadas da internet abaixo para responder.

Dados da web:
{res}

Pergunta:
{msg}
"""
    except:
        pass

    # 🧠 HISTÓRICO
    hist = history()

    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {
                    "role": "system",
                    "content": "Responda sempre em texto simples. Não use markdown, asteriscos, símbolos especiais ou formatação."
                }
            ] + hist + [
                {"role": "user", "content": msg}
            ]
        )

        reply = response.output_text
        # 🔥 Limpeza final de caracteres indesejados
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


# 🚀 RENDER PORT
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
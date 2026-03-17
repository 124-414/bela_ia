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

    # 🌍 BUSCA FORÇADA NA INTERNET
    try:
        res = google_search(msg_original)

        if res and len(res.strip()) > 50:
            msg_final = f"""
Você DEVE responder usando SOMENTE as informações abaixo.

DADOS DA INTERNET:
{res}

PERGUNTA:
{msg_original}
"""
    except Exception as e:
        print("Erro na busca:", e)

    hist = history()[-5:]

    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {
                    "role": "system",
                    "content": "Responda direto. Nunca diga que não tem acesso à internet."
                }
            ] + hist + [
                {"role": "user", "content": msg_final}
            ]
        )

        reply = response.output_text

        # limpeza
        reply = re.sub(r'[\*_`]', '', reply)

        # bloqueio de resposta errada
        if "não tenho acesso" in reply.lower():
            reply = "Erro: busca não aplicada."

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
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

# 🔑 Cliente OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 📦 Inicializar banco
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

    # 🖼 Imagem
    if msg.startswith("imagem:"):
        prompt = msg.replace("imagem:", "").strip()
        url = create_image(prompt)

        reply = f"<img src='{url}' width='300'>"
        save("assistant", reply)

        return jsonify({"response": reply})

    # 🌍 Google
    if msg.startswith("google:"):
        q = msg.replace("google:", "").strip()
        res = google_search(q)
        msg = f"Resultados da web:\n{res}"

    # 🧠 Histórico
    hist = history()

    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=hist + [{"role": "user", "content": msg}]
        )

        reply = response.output_text

    except Exception as e:
        reply = f"Erro na IA: {str(e)}"

    save("assistant", reply)

    return jsonify({"response": reply})


# 📂 Upload PDF
@app.route("/upload", methods=["POST"])
def upload():

    if "file" not in request.files:
        return jsonify({"text": "Nenhum arquivo enviado."})

    file = request.files["file"]
    text = read_pdf(file)

    return jsonify({"text": text})


# 🚀 PORTA DO RENDER
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
import os
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import requests
from datetime import datetime
import pytz
from openai import OpenAI

# 🔐 Carrega .env
load_dotenv()

app = Flask(__name__)

# 🧠 OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ==============================
# 📰 BUSCAR NOTÍCIAS (NEWSAPI)
# ==============================
def buscar_noticias(query):
    api_key = os.getenv("NEWS_API_KEY")

    if not api_key:
        return ""

    url = "https://newsapi.org/v2/everything"

    params = {
        "q": query,
        "language": "pt",
        "sortBy": "publishedAt",
        "pageSize": 3,
        "apiKey": api_key
    }

    try:
        response = requests.get(url, params=params, timeout=8)
        data = response.json()

        if data.get("status") != "ok":
            return ""

        artigos = data.get("articles", [])

        textos = []
        for art in artigos:
            titulo = art.get("title", "")
            fonte = art.get("source", {}).get("name", "")
            link = art.get("url", "")
            textos.append(f"{titulo} ({fonte})\n{link}")

        return "\n\n".join(textos)

    except Exception as e:
        print("Erro NewsAPI:", e)
        return ""

# ==============================
# 🏠 PÁGINA INICIAL
# ==============================
@app.route("/")
def home():
    return render_template("index.html")

# ==============================
# 💬 CHAT
# ==============================
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")

    # ⏰ Horário de Brasília
    brasilia = pytz.timezone("America/Sao_Paulo")
    agora = datetime.now(brasilia)
    hora_formatada = agora.strftime("%d/%m/%Y %H:%M:%S")

    # 📰 Buscar notícias
    noticias = buscar_noticias(user_message)

    contexto = f"Data e hora atual (Brasília): {hora_formatada}\n"

    if noticias:
        contexto += f"\nNotícias recentes encontradas:\n{noticias}\n"

    try:
        resposta = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Você é a Bela, uma IA que usa informações atualizadas quando fornecidas."
                },
                {
                    "role": "user",
                    "content": contexto + "\nPergunta: " + user_message
                }
            ]
        )

        texto = resposta.choices[0].message.content

    except Exception as e:
        print("Erro OpenAI:", e)
        texto = "Erro ao gerar resposta."

    return jsonify({"response": texto})

# ==============================
# 🚀 EXECUÇÃO
# ==============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
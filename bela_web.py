import os
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import requests
from datetime import datetime
import pytz
from openai import OpenAI

# 🔐 Carrega variáveis
load_dotenv()

app = Flask(__name__)

# 🧠 OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ==============================
# 📰 BUSCAR NOTÍCIAS
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
# 🏠 HOME
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

    # ⏰ Hora Brasília
    brasilia = pytz.timezone("America/Sao_Paulo")
    agora = datetime.now(brasilia)
    hora_formatada = agora.strftime("%d/%m/%Y %H:%M:%S")

    # 📰 Notícias
    noticias = buscar_noticias(user_message)

    contexto = f"""
Data e hora atual (Brasília): {hora_formatada}

Notícias recentes:
{noticias if noticias else "Nenhuma notícia encontrada"}
"""

    try:
        resposta = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """Você é a Bela, uma IA atualizada.

SEMPRE use as notícias fornecidas.
Se houver notícias, nunca diga que não tem acesso à internet.
Responda com base nelas.

Se não houver notícias, responda normalmente."""
                },
                {
                    "role": "user",
                    "content": f"""
{contexto}

Pergunta:
{user_message}

Responda de forma clara e atual.
"""
                }
            ]
        )

        texto = resposta.choices[0].message.content

    except Exception as e:
        print("Erro OpenAI:", e)
        texto = f"Erro: {str(e)}"

    return jsonify({"response": texto})

# ==============================
# 🚀 RUN
# ==============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
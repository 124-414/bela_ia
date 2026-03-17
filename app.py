import os
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import requests
from openai import OpenAI

# 🔐 Carrega variáveis locais (.env)
load_dotenv()

app = Flask(__name__)

# 🧠 OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ==============================
# 🌐 BUSCA DE NOTÍCIAS
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
        response = requests.get(url, params=params, timeout=5)
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

    except:
        return ""


# ==============================
# 🔎 DETECTA SE PRECISA WEB
# ==============================

def precisa_buscar(texto):
    palavras = [
        "noticia", "notícias", "hoje", "atual",
        "guerra", "prefeito", "presidente",
        "últimas", "recente"
    ]

    texto = texto.lower()
    return any(p in texto for p in palavras)


# ==============================
# 🏠 PÁGINA PRINCIPAL
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

    contexto = ""

    # 🔥 Se for pergunta que precisa de notícias
    if precisa_buscar(user_message):
        noticias = buscar_noticias(user_message)
        if noticias:
            contexto = f"""
Use as informações abaixo para responder:

{noticias}

"""

    try:
        resposta = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Você é uma IA profissional com acesso a ferramentas e informações atualizadas."
                },
                {
                    "role": "user",
                    "content": contexto + user_message
                }
            ]
        )

        texto = resposta.choices[0].message.content

    except Exception as e:
        texto = "Erro ao gerar resposta."

    return jsonify({"response": texto})


# ==============================
# 🚀 INICIALIZAÇÃO CORRETA
# ==============================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
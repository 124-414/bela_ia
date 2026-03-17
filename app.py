import os
import requests
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from openai import OpenAI

# 🔐 carregar .env
load_dotenv()

app = Flask(__name__)

# 🔑 OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 🌐 FUNÇÃO DE NOTÍCIAS (PROFISSIONAL)
def buscar_noticias(query):
    api_key = os.getenv("NEWS_API_KEY")

    if not api_key:
        print("❌ NEWS_API_KEY não encontrada")
        return ""

    url = "https://newsapi.org/v2/everything"

    params = {
        "q": query,
        "language": "pt",
        "sortBy": "publishedAt",
        "pageSize": 5,
        "apiKey": api_key
    }

    try:
        res = requests.get(url, params=params, timeout=5)
        data = res.json()

        artigos = data.get("articles", [])

        if not artigos:
            return ""

        textos = []
        for art in artigos:
            titulo = art.get("title", "")
            fonte = art.get("source", {}).get("name", "")
            link = art.get("url", "")

            textos.append(f"• {titulo} ({fonte})\n{link}")

        return "\n\n".join(textos)

    except Exception as e:
        print("Erro NewsAPI:", e)
        return ""


# 🧠 DETECTOR INTELIGENTE (QUANDO USAR WEB)
def precisa_buscar(msg):
    palavras = [
        "noticia", "notícias", "hoje", "agora",
        "atual", "guerra", "prefeito", "presidente",
        "acontecendo", "últimas", "recente"
    ]

    msg = msg.lower()
    return any(p in msg for p in palavras)


# 🏠 FRONT
@app.route("/")
def index():
    return render_template("index.html")


# 💬 CHAT
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_msg = data.get("message", "")

    contexto = ""

    # 🔥 BUSCA AUTOMÁTICA
    if precisa_buscar(user_msg):
        noticias = buscar_noticias(user_msg)

        if noticias:
            contexto = f"""
Use APENAS as informações abaixo para responder com base em fatos atuais:

{noticias}

Responda de forma clara e objetiva.
"""
        else:
            contexto = "Não foram encontradas notícias recentes confiáveis."

    try:
        resposta = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Você é uma IA inteligente que responde de forma clara e profissional."
                },
                {
                    "role": "user",
                    "content": contexto + "\n\n" + user_msg
                }
            ]
        )

        texto = resposta.choices[0].message.content

    except Exception as e:
        print("Erro OpenAI:", e)
        texto = "Erro ao processar resposta."

    return jsonify({"response": texto})


# 🚀 RUN LOCAL
if __name__ == "__main__":
    app.run(debug=True)
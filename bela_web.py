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

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ==============================
# 📰 BUSCAR NOTÍCIAS
# ==============================
def buscar_noticias(query):
    api_key = os.getenv("NEWS_API_KEY")

    if not api_key:
        return []

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
            return []

        return data.get("articles", [])

    except Exception as e:
        print("Erro NewsAPI:", e)
        return []

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

    # ⏰ Hora
    brasilia = pytz.timezone("America/Sao_Paulo")
    agora = datetime.now(brasilia)
    hora = agora.strftime("%d/%m/%Y %H:%M:%S")

    # 🔎 detectar se precisa notícia
    palavras = ["notícia", "noticias", "guerra", "hoje", "atual", "acontecendo"]

    artigos = []
    if any(p in user_message.lower() for p in palavras):
        artigos = buscar_noticias(user_message)

    # 🔥 MONTA CONTEXTO CONTROLADO
    contexto = f"Data atual: {hora}\n"

    if artigos:
        contexto += "\nNOTÍCIAS REAIS:\n"
        for art in artigos:
            contexto += f"- {art.get('title')} ({art.get('source', {}).get('name')})\n"
            contexto += f"{art.get('url')}\n\n"

    try:
        resposta = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """Você é a Bela, uma IA precisa e confiável.

REGRAS ABSOLUTAS:
- Use SOMENTE as notícias fornecidas.
- NÃO invente nenhuma informação.
- Se houver notícias, baseie-se APENAS nelas.
- Se NÃO houver notícias, IGNORE completamente esse assunto.
- Para perguntas gerais (ex: política, pessoas), responda normalmente.
- Se não souber algo, diga claramente.

Seja objetiva e correta."""
                },
                {
                    "role": "user",
                    "content": f"""
{contexto}

Pergunta:
{user_message}
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
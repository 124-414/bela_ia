import os
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from openai import OpenAI

# 🔐 Carrega variáveis locais (.env)
load_dotenv()

app = Flask(__name__)

# 🧠 OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ==============================
# 🌐 FUNÇÃO PARA BUSCAR NOTÍCIAS
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
        textos = [
            f"{art.get('title','')} ({art.get('source',{}).get('name','')})\n{art.get('url','')}"
            for art in artigos
        ]
        return "\n\n".join(textos)
    except:
        return ""

# ==============================
# 🔎 FUNÇÃO PARA DETERMINAR SE PRECISA DE WEB
# ==============================
def precisa_buscar(texto):
    palavras = [
        "noticia", "notícias", "hoje", "atual",
        "guerra", "prefeito", "presidente",
        "últimas", "recente", "cotação", "tempo", "clima"
    ]
    texto = texto.lower()
    return any(p in texto for p in palavras)

# ==============================
# 🔎 FUNÇÃO DE PESQUISA NO GOOGLE
# ==============================
def google_search(query):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        url = f"https://www.google.com/search?q={query}&hl=pt-BR"
        response = requests.get(url, headers=headers, timeout=4)
        soup = BeautifulSoup(response.text, "html.parser")

        results = []
        for div in soup.find_all("div"):
            text = div.get_text()
            if len(text) > 80:
                results.append(text)
        return "\n".join(results[:3])
    except:
        return ""

# ==============================
# 🏠 PÁGINA PRINCIPAL
# ==============================
@app.route("/")
def home():
    return render_template("index.html")

# ==============================
# 💬 CHAT COM ACESSO A WEB E DATA/HORA
# ==============================
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")

    # 🔥 Contexto inicial
    agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    contexto = f"Data e hora atual: {agora}\n"

    # 🔥 Busca de notícias ou pesquisa
    if precisa_buscar(user_message):
        noticias = buscar_noticias(user_message)
        if noticias:
            contexto += f"\nInformações recentes encontradas:\n{noticias}\n"
        else:
            pesquisa = google_search(user_message)
            if pesquisa:
                contexto += f"\nResultados da web:\n{pesquisa}\n"

    try:
        resposta = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Você é uma IA profissional com acesso a informações atualizadas e ferramentas de pesquisa na web."
                },
                {
                    "role": "user",
                    "content": contexto + user_message
                }
            ]
        )
        texto = resposta.choices[0].message.content
    except Exception as e:
        print("Erro OpenAI:", e)
        texto = "Erro ao gerar resposta."

    return jsonify({"response": texto})

# ==============================
# 🚀 INICIALIZAÇÃO
# ==============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
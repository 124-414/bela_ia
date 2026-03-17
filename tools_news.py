import os
import requests

def buscar_noticias(query):
    api_key = os.getenv("NEWS_API_KEY")

    if not api_key:
        print("SEM API KEY")
        return ""

    url = "https://newsapi.org/v2/everything"

    params = {
        "q": query,
        "language": "pt,en",
        "sortBy": "publishedAt",
        "pageSize": 5,
        "apiKey": api_key
    }

    try:
        res = requests.get(url, params=params, timeout=5)
        data = res.json()

        print("RESPOSTA API:", data)  # 🔍 debug

        artigos = data.get("articles", [])

        if not artigos:
            return ""

        textos = []
        for art in artigos:
            titulo = art.get("title", "")
            descricao = art.get("description", "")
            fonte = art.get("source", {}).get("name", "")
            link = art.get("url", "")

            textos.append(f"{titulo} - {descricao} ({fonte}) {link}")

        return "\n".join(textos)

    except Exception as e:
        print("ERRO NEWS:", e)
        return ""
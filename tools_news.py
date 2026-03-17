import os
import requests

def buscar_noticias(query):
    api_key = os.getenv("NEWS_API_KEY")

    if not api_key:
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
            titulo = art["title"]
            fonte = art["source"]["name"]
            textos.append(f"{titulo} ({fonte})")

        return "\n".join(textos)

    except:
        return ""
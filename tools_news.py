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
        "pageSize": 3,
        "apiKey": api_key
    }

    try:
        res = requests.get(url, params=params, timeout=5)
        data = res.json()

        if data.get("status") != "ok":
            return ""

        artigos = data.get("articles", [])

        textos = []
        for art in artigos:
            textos.append(
                f"{art['title']} ({art['source']['name']})\n{art['url']}"
            )

        return "\n\n".join(textos)

    except:
        return ""
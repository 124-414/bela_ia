import requests

def google_search(query):

    try:
        url = "https://api.duckduckgo.com/"

        params = {
            "q": query,
            "format": "json",
            "no_html": 1,
            "skip_disambig": 1
        }

        r = requests.get(url, params=params, timeout=10)

        if r.status_code != 200:
            return ""

        data = r.json()

        results = []

        # Resumo principal
        if data.get("AbstractText"):
            results.append(data["AbstractText"])

        # Tópicos relacionados
        for topic in data.get("RelatedTopics", [])[:5]:
            if isinstance(topic, dict) and topic.get("Text"):
                results.append(topic["Text"])

        return "\n".join(results)

    except Exception as e:
        print("Erro na busca:", e)
        return ""
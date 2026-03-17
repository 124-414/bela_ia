import requests
from bs4 import BeautifulSoup


def google_search(query):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        url = f"https://www.google.com/search?q={query}&hl=pt-BR"

        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        results = []

        for g in soup.find_all("div", class_="BNeawe s3v9rd AP7Wnd"):
            text = g.get_text()
            if len(text) > 50:
                results.append(text)

        return "\n".join(results[:5])

    except Exception as e:
        print("Erro Google:", e)
        return ""
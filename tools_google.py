import requests
from bs4 import BeautifulSoup

def google_search(query):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        url = f"https://www.google.com/search?q={query}&hl=pt-BR"

        # 🔥 TIMEOUT EVITA TRAVAMENTO
        response = requests.get(url, headers=headers, timeout=4)

        soup = BeautifulSoup(response.text, "html.parser")

        results = []

        for div in soup.find_all("div"):
            text = div.get_text()
            if len(text) > 80:
                results.append(text)

        return "\n".join(results[:3])

    except Exception as e:
        print("Erro Google:", e)
        return ""
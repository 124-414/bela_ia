import requests
from bs4 import BeautifulSoup
import urllib.parse


def google_search(query):

    try:
        # Codifica a busca corretamente
        query_encoded = urllib.parse.quote_plus(query)

        url = f"https://www.google.com/search?q={query_encoded}&hl=pt"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }

        # Timeout é importante em produção
        r = requests.get(url, headers=headers, timeout=10)

        # Se for bloqueado, retorna erro
        if r.status_code != 200:
            return ""

        soup = BeautifulSoup(r.text, "html.parser")

        results = []

        # Seletores mais amplos
        for item in soup.select("div.BNeawe")[:5]:
            texto = item.get_text().strip()
            if texto:
                results.append(texto)

        return "\n".join(results)

    except Exception as e:
        print("Erro na busca:", e)
        return ""
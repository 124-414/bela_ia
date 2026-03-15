import os
from serpapi import GoogleSearch


def buscar_web(query: str):

    try:

        params = {
            "engine": "google",
            "q": query,
            "api_key": os.getenv("SERPAPI_KEY"),
        }

        search = GoogleSearch(params)
        results = search.get_dict()

        if "organic_results" in results and len(results["organic_results"]) > 0:

            primeiro = results["organic_results"][0]

            titulo = primeiro.get("title", "")
            snippet = primeiro.get("snippet", "")

            return f"{titulo}\n{snippet}"

        return "Nenhum resultado encontrado."

    except Exception as e:
        return f"Erro na busca: {str(e)}"
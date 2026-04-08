from wikipediaapi import Wikipedia

def buscar_wikipedia(query: str) -> str:
    wiki = Wikipedia(user_agent="BelaAI/1.0 (meuemail@example.com)", language="pt")
    # Limpa a query para melhorar a busca
    termo = query.replace("quem é", "").replace("prefeito de", "").strip()
    page = wiki.page(termo)
    if page.exists():
        return page.summary[0:800]
    return ""
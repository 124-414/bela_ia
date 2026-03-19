from wikipediaapi import Wikipedia

def buscar_wikipedia(query: str) -> str:
    wiki = Wikipedia(user_agent="BelaAI/1.0 (meuemail@example.com)", language="pt")
    page = wiki.page(query)
    if page.exists():
        return page.summary[0:800]  # limitar tamanho da resposta
    return ""
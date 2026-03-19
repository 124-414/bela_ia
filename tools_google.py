import os
import requests
from dotenv import load_dotenv

load_dotenv()

def pesquisar_google(query):
    api_key = os.getenv("NEWS_API_KEY")
    if not api_key:
        return ""

    # Limpeza para focar no assunto real (Cidade, Político, Evento)
    remover = ["bela", "confirme", "para", "mim", "quem", "é", "o", "atual", "qual", "fuso", "horário", "de", "do", "da"]
    palavras = query.lower().split()
    query_busca = " ".join([p for p in palavras if p not in remover]).strip()

    # Tenta buscar em 'everything' para máxima cobertura global
    url = f"https://newsapi.org/v2/everything?q={query_busca}&language=pt&sortBy=publishedAt&apiKey={api_key}"
    
    try:
        print(f"\n[SISTEMA WEB] Pesquisando globalmente: '{query_busca}'...")
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        
        if response.status_code == 200:
            artigos = response.json().get("articles", [])
            if artigos:
                print(f"[SISTEMA WEB] Sucesso! Encontrei dados sobre '{query_busca}'.")
                contexto = "INFORMAÇÕES RECENTES DA WEB (2025-2026):\n"
                for art in artigos[:3]:
                    contexto += f"- {art['title']}: {art['description']}\n"
                return contexto
        print(f"[SISTEMA WEB] Sem notícias recentes para '{query_busca}'.")
        return ""
    except:
        return ""
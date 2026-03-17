from tools_news import buscar_noticias
from tools_google import buscar_web

def precisa_noticias(texto):
    palavras = ["noticia", "notícias", "hoje", "atual", "guerra", "prefeito", "presidente"]
    texto = texto.lower()
    return any(p in texto for p in palavras)

def executar_tools(mensagem):
    resultado = ""

    if precisa_noticias(mensagem):
        noticias = buscar_noticias(mensagem)
        if noticias:
            resultado += f"\nNOTÍCIAS ENCONTRADAS:\n{noticias}\n"

    # Se quiser adicionar Google:
    # resultado += buscar_web(mensagem)

    return resultado
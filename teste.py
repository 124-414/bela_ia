from ddgs import DDGS

with DDGS() as ddgs:
    resultados = ddgs.text("Python programação", max_results=5)

    for r in resultados:
        print("Título:", r["title"])
        print("Link:", r["href"])
        print("Resumo:", r["body"])
        print("-" * 50)
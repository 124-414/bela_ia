import requests
import pdfplumber
from io import BytesIO

# 📄 Link do PDF
url = "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"

# Baixar PDF
response = requests.get(url)

# Extrair todo o texto
texto_completo = ""

with pdfplumber.open(BytesIO(response.content)) as pdf:
    for pagina in pdf.pages:
        texto = pagina.extract_text()
        if texto:
            texto_completo += texto + "\n"

# Loop de perguntas
while True:
    pergunta = input("\nVocê: ").lower()

    if pergunta in ["sair", "exit"]:
        break

    if "o que" in pergunta or "resumo" in pergunta:
        print("\nBela: O documento contém o seguinte texto:")
        print(texto_completo[:500])  # mostra parte do texto

    elif "tem" in pergunta:
        palavra = pergunta.replace("tem", "").strip()

        if palavra in texto_completo.lower():
            print(f"\nBela: Sim, encontrei '{palavra}' no documento.")
        else:
            print(f"\nBela: Não encontrei '{palavra}' no documento.")

    else:
        print("\nBela: Não entendi a pergunta.")
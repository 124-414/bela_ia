import os
import re
import PyPDF2
import unicodedata
from flask import Flask, request, jsonify, render_template
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__, template_folder='templates')
historico_global = []

def extrair_radical(palavra):
    """
    Transforma 'Espaçadores' em 'espacador', 'Chaves' em 'chave',
    'Substituição' em 'substitu'. Isso cria o DISCERNIMENTO de busca.
    """
    if not palavra: return ""
    # Remove acentos e símbolos
    p = "".join(c for c in unicodedata.normalize('NFKD', palavra) if not unicodedata.combining(c))
    p = p.lower().strip()
    
    # Regras de Radicalização (Stemming manual)
    if len(p) > 5:
        p = p.replace('coes', 'cao').replace('icao', 'icu')
        if p.endswith('s'): p = p[:-1] # Remove plural
        if p.endswith('es'): p = p[:-2]
        if p.endswith('ar') or p.endswith('er') or p.endswith('ir'): p = p[:-2] # Remove sufixo de verbo
    return re.sub(r'[^a-z0-9]', '', p)

def buscar_it_com_discernimento(mensagem):
    """Varre os arquivos buscando o radical das palavras, ignorando plural e conjugação."""
    base_path = os.path.dirname(os.path.abspath(__file__))
    diretorio_docs = os.path.join(base_path, "docs")
    subpastas = ["linha_morta", "linha_viva"]
    
    termos_pergunta = [extrair_radical(t) for t in mensagem.split() if len(t) > 2]
    
    melhor_it = None
    maior_pontuacao = 0

    if not os.path.exists(diretorio_docs): return None

    for sub in subpastas:
        pasta = os.path.join(diretorio_docs, sub)
        if not os.path.exists(pasta): continue
        
        for arq in os.listdir(pasta):
            if arq.lower().endswith(".pdf"):
                nome_arq_radical = extrair_radical(arq)
                # O discernimento acontece aqui: comparamos radicais
                pontos = sum(1 for termo in termos_pergunta if termo in nome_arq_radical)
                
                # Se houver número na pergunta, ele vale 10 pontos (prioridade total)
                numeros_pergunta = re.findall(r'\d+', mensagem)
                for num in numeros_pergunta:
                    if num in arq: pontos += 10

                if pontos > maior_pontuacao:
                    maior_pontuacao = pontos
                    melhor_it = os.path.join(pasta, arq)

    if melhor_it and maior_pontuacao > 0:
        try:
            print(f">>> VÍNCULO ASSIMILADO: {os.path.basename(melhor_it)} (Pontos: {maior_pontuacao})")
            with open(melhor_it, 'rb') as f:
                leitor = PyPDF2.PdfReader(f)
                texto = ""
                for i in range(min(15, len(leitor.pages))):
                    texto += leitor.pages[i].extract_text() or ""
                return f"--- ARQUIVO: {os.path.basename(melhor_it)} ---\n{texto}"
        except: return None
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    global historico_global
    try:
        dados = request.json
        pergunta = dados.get("message", "")
        
        # Aqui a Bela usa o discernimento para achar o PDF
        conhecimento_pdf = buscar_it_com_discernimento(pergunta)
        
        if conhecimento_pdf:
            system_msg = (
                "Você é a BELA, especialista técnica da Energisa. "
                "Responda detalhadamente com base no PDF identificado. "
                "Sua missão principal é a SEQUÊNCIA DE TAREFAS. "
                "Não responda com base em conhecimentos gerais, apenas no PDF."
                f"\n\n[DADOS DO PDF]:\n{conhecimento_pdf}"
            )
        else:
            system_msg = "Diga que não localizou uma IT com esses termos exatos na pasta docs."

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": system_msg}] + historico_global[-2:] + [{"role": "user", "content": pergunta}],
            temperature=0
        )
        
        res = response.choices[0].message.content
        historico_global.append({"role": "user", "content": pergunta})
        historico_global.append({"role": "assistant", "content": res})
        if len(historico_global) > 4: historico_global = historico_global[-4:]

        return jsonify({"response": res})
    except Exception as e:
        print(f">>> ERRO: {e}")
        return jsonify({"response": "Erro ao assimilar termos técnicos."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)
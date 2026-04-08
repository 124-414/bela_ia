import os, re, json, PyPDF2, unicodedata
from datetime import datetime, timedelta, timezone
from flask import Flask, request, jsonify, render_template
from openai import OpenAI
from dotenv import load_dotenv
from tools_wikipedia import buscar_wikipedia

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__, template_folder='templates', static_folder='static')
historico_global = []

def extrair_radical(palavra):
    if not palavra: return ""
    p = "".join(c for c in unicodedata.normalize('NFKD', palavra) if not unicodedata.combining(c))
    p = p.lower().strip()
    if len(p) > 4 and p.endswith('s'): p = p[:-1]
    return re.sub(r'[^a-z0-9]', '', p)

def buscar_it_pdf(mensagem):
    base_path = os.path.dirname(os.path.abspath(__file__))
    diretorio_docs = os.path.join(base_path, "docs")
    if not os.path.exists(diretorio_docs): return None
    numeros = re.findall(r'\d+', mensagem)
    termos = [extrair_radical(t) for t in mensagem.split() if len(t) > 3]
    melhor_match, maior_pontuacao = None, 0
    for root, dirs, files in os.walk(diretorio_docs):
        for arq in files:
            if arq.lower().endswith(".pdf"):
                pontos = sum(200 for n in numeros if n in arq)
                pontos += sum(40 for t in termos if t in extrair_radical(arq))
                if pontos > maior_pontuacao:
                    maior_pontuacao, melhor_match = pontos, os.path.join(root, arq)
    if melhor_match and maior_pontuacao >= 100:
        try:
            with open(melhor_match, 'rb') as f:
                leitor = PyPDF2.PdfReader(f)
                return f"--- CONTEÚDO TÉCNICO PDF: {os.path.basename(melhor_match)} ---\n" + \
                       "".join([p.extract_text() for p in leitor.pages[:35]])
        except: return None
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    global historico_global
    try:
        data = request.json
        pergunta = data.get("message", "").strip()
        pergunta_lower = pergunta.lower()
        agora = datetime.now(timezone(timedelta(hours=-4))).strftime("%H:%M de %d/%m/%Y")

        # RAG - Busca Inteligente
        contexto_pdf = buscar_it_pdf(pergunta_lower) if any(x in pergunta_lower for x in ["it", "nº", "tecnica"]) else None
        contexto_web = buscar_wikipedia(pergunta) if not contexto_pdf else ""

        system_msg = (
            f"IDENTIDADE: BELA. DATA: {agora}. LOCAL: Rondônia.\n"
            "MISSÃO: Você é uma Analista Sênior de Dados e Geopolítica.\n"
            "COMPORTAMENTO:\n"
            "1. Seja educada, responda saudações, mas seja extremamente técnica em perguntas complexas.\n"
            "2. ANO ATUAL: 2026. Use o [CONTEÚDO WEB] como base para fatos recentes.\n"
            "3. PRECISÃO: Evite respostas genéricas. Se o contexto trouxer números ou nomes de leis, cite-os.\n"
            "4. FORMATO: Não repita a pergunta do usuário. Se houver uma lista, apenas numere as respostas.\n"
            "5. Se o dado não existir de forma alguma na Web, explique o cenário provável com base em indicadores reais de 2025."
        )

        prompt_final = system_msg
        if contexto_web: prompt_final += f"\n[PESQUISA WEB ATUAL]: {contexto_web}"
        if contexto_pdf: prompt_final += f"\n[DOC TÉCNICO]: {contexto_pdf}"

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": prompt_final}] + historico_global[-6:] + [{"role": "user", "content": pergunta}],
            temperature=0.6 # Ideal para manter a fluidez sem perder a linha lógica
        )

        res = response.choices[0].message.content
        historico_global.append({"role": "user", "content": pergunta})
        historico_global.append({"role": "assistant", "content": res})
        if len(historico_global) > 12: historico_global = historico_global[-12:]

        return jsonify({"response": res})
    except Exception as e:
        return jsonify({"response": f"Erro: {str(e)}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)
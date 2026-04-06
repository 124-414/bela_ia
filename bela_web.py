import os
import re
import PyPDF2
import unicodedata
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from openai import OpenAI
from dotenv import load_dotenv

# 1. INICIALIZAÇÃO
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__, template_folder='templates')
historico_global = []

def extrair_radical(palavra):
    if not palavra: return ""
    p = "".join(c for c in unicodedata.normalize('NFKD', palavra) if not unicodedata.combining(c))
    p = p.lower().strip()
    if len(p) > 4:
        if p.endswith('s'): p = p[:-1]
    return re.sub(r'[^a-z0-9]', '', p)

def buscar_it_automatico(mensagem):
    base_path = os.path.dirname(os.path.abspath(__file__))
    diretorio_docs = os.path.join(base_path, "docs")
    if not os.path.exists(diretorio_docs): return None

    numeros = re.findall(r'\d+', mensagem)
    termos = [extrair_radical(t) for t in mensagem.split() if len(t) > 3]
    
    melhor_match = None
    maior_pontuacao = 0

    for root, dirs, files in os.walk(diretorio_docs):
        for arq in files:
            if arq.lower().endswith(".pdf"):
                pontos = 0
                for n in numeros:
                    if n in arq: pontos += 100
                pontos += sum(25 for t in termos if t in extrair_radical(arq))
                if pontos > maior_pontuacao:
                    maior_pontuacao = pontos
                    melhor_match = os.path.join(root, arq)
    
    if melhor_match and maior_pontuacao >= 80:
        try:
            with open(melhor_match, 'rb') as f:
                leitor = PyPDF2.PdfReader(f)
                conteudo = f"--- DOC ENCONTRADO: {os.path.basename(melhor_match)} ---\n"
                conteudo += "".join([p.extract_text() for p in leitor.pages[:10]])
                return conteudo
        except: return None
    return None

# 2. ROTAS
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    global historico_global
    try:
        dados = request.json
        pergunta = dados.get("message", "")
        pergunta_lower = pergunta.lower()
        agora = datetime.now().strftime("%H:%M de %d/%m/%Y")
        
        conhecimento = None
        palavras_it = ["it", "norma", "instrucao", "procedimento", "como fazer"]
        if any(p in pergunta_lower for p in palavras_it) or any(c.isdigit() for c in pergunta):
            conhecimento = buscar_it_automatico(pergunta_lower)

        # 3. SYSTEM PROMPT REFINADO (REMOÇÃO DE ASTERISCOS E RIGOR TOTAL)
        system_msg = (
            f"Você é a BELA, assistente oficial da Energisa. Data: {agora}. "
            "Você atende sob coordenação do Valdimar (Valdi). "
            "\n\nREGRAS DE OURO:"
            "\n1. SEM FORMATAÇÃO: NUNCA use asteriscos (**), cerquilhas (#) ou Markdown. Responda apenas com texto limpo e parágrafos."
            "\n2. RIGOR E ASSERTIVIDADE: Respostas diretas, factuais e com alto rigor técnico."
            "\n3. PADRÃO DE E-MAIL: Assunto, Saudação, Corpo e uma Despedida única. Sem numeração automática."
            "\n4. NUMERAÇÃO: Use listas (1, 2, 3...) somente se o usuário pedir explicitamente 'numere' ou 'liste'."
            "\n5. CONTEXTO: Use os [DADOS TÉCNICOS] se disponíveis para extrair o passo a passo fiel da Energisa."
        )
        
        if conhecimento:
            system_msg += f"\n\n[DADOS TÉCNICOS]:\n{conhecimento}"

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": system_msg}] + historico_global[-12:] + [{"role": "user", "content": pergunta}],
            temperature=0.3 # Baixa temperatura para garantir o cumprimento das regras de formatação
        )
        
        res = response.choices[0].message.content
        
        # Limpeza extra via código para garantir que nenhum asterisco escape
        res = res.replace("**", "").replace("__", "")

        historico_global.append({"role": "user", "content": pergunta})
        historico_global.append({"role": "assistant", "content": res})
        if len(historico_global) > 20: historico_global = historico_global[-20:]

        return jsonify({"response": res})
    except Exception as e:
        return jsonify({"response": f"Erro: {str(e)}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)
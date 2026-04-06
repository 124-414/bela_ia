import os
import re
import PyPDF2
import unicodedata
from datetime import datetime, timedelta, timezone
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

def buscar_it_profundo(mensagem):
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
                conteudo = f"--- DOCUMENTO TÉCNICO: {os.path.basename(melhor_match)} ---\n"
                # Lendo até 25 páginas para garantir que pegamos os detalhes do final
                limite = min(len(leitor.pages), 25)
                conteudo += "".join([p.extract_text() for p in leitor.pages[:limite]])
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
        
        fuso_rondonia = timezone(timedelta(hours=-4))
        agora = datetime.now(fuso_rondonia).strftime("%H:%M de %d/%m/%Y")
        
        conhecimento = None
        if any(x in pergunta_lower for x in ["it", "página", "norma", "passo"]) or any(c.isdigit() for c in pergunta):
            conhecimento = buscar_it_profundo(pergunta_lower)

        # 3. SYSTEM PROMPT - RIGOR PARA TREINAMENTO
        system_msg = (
            f"Você é a BELA, assistente virtual técnica de alto nível. Agora são {agora} em Rondônia. "
            "\n\nREGRAS DE OURO PARA TREINAMENTO:"
            "\n1. RIGOR TÉCNICO TOTAL: Se houver [DADOS TÉCNICOS], ignore conhecimentos genéricos da internet. Use APENAS o que está no texto do PDF. Cite ferramentas específicas e nomes de nós/procedimentos que constarem lá."
            "\n2. SEM DESCULPAS: Nunca diga 'não tenho acesso' ou 'posso sugerir um padrão' se o dado técnico estiver presente abaixo. Se o dado estiver presente, você TEM acesso."
            "\n3. FORMATAÇÃO LIMPA: Proibido o uso de asteriscos (**), cerquilhas (#) ou Markdown. Use apenas texto e parágrafos fluidos."
            "\n4. ASSERTIVIDADE: Seja direta. Para treinamentos, o usuário quer o passo a passo fiel à norma, sem enrolação e sem formato de e-mail."
        )
        
        if conhecimento:
            system_msg += f"\n\n[DADOS TÉCNICOS EXTRAÍDOS]:\n{conhecimento}"

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": system_msg}] + historico_global[-10:] + [{"role": "user", "content": pergunta}],
            temperature=0.1 # Temperatura mínima para evitar qualquer "criatividade"
        )
        
        res = response.choices[0].message.content
        res = res.replace("**", "").replace("__", "").replace("#", "")

        historico_global.append({"role": "user", "content": pergunta})
        historico_global.append({"role": "assistant", "content": res})
        if len(historico_global) > 20: historico_global = historico_global[-20:]

        return jsonify({"response": res})
    except Exception as e:
        return jsonify({"response": f"Erro: {str(e)}"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5001))
    app.run(host='0.0.0.0', port=port, debug=False)
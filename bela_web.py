import os, base64, re, PyPDF2, unicodedata
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

try:
    from tools_image import create_image
except ImportError:
    def create_image(prompt): return None

app = Flask(__name__)

# MEMÓRIA GLOBAL
historico_global = []

def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

def extrair_radical(palavra):
    if not palavra: return ""
    p = "".join(c for c in unicodedata.normalize('NFKD', palavra) if not unicodedata.combining(c))
    p = p.lower().strip()
    return re.sub(r'[^a-z0-9]', '', p)

def buscar_it_pdf(mensagem):
    base_path = os.path.dirname(os.path.abspath(__file__))
    diretorio_docs = os.path.join(base_path, "docs")
    if not os.path.exists(diretorio_docs): return None
    
    termos = [extrair_radical(t) for t in mensagem.split() if len(t) > 2]
    melhor_match, maior_pontuacao = None, 0
    
    for root, dirs, files in os.walk(diretorio_docs):
        for arq in files:
            if arq.lower().endswith(".pdf"):
                pontos = sum(50 for t in termos if t in extrair_radical(arq))
                if pontos > maior_pontuacao:
                    maior_pontuacao, melhor_match = pontos, os.path.join(root, arq)
    
    if melhor_match and maior_pontuacao > 0:
        try:
            with open(melhor_match, 'rb') as f:
                leitor = PyPDF2.PdfReader(f)
                return f"--- CONTEÚDO TÉCNICO ENCONTRADO ({os.path.basename(melhor_match)}) ---\n" + \
                       "".join([p.extract_text() for p in leitor.pages[:10]])
        except: return None
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    global historico_global
    try:
        pergunta = request.form.get("message", "").strip()
        arquivo = request.files.get("file")
        pergunta_lower = pergunta.lower()
        
        agora = datetime.now(timezone(timedelta(hours=-3)))
        timestamp = agora.strftime('%H:%M de %d/%m/%Y')

        if any(k in pergunta_lower for k in ["imagem", "foto", "gerar", "desenhe", "crie uma imagem"]) and not arquivo:
            url = create_image(pergunta)
            if url:
                historico_global.append({"role": "user", "content": pergunta})
                historico_global.append({"role": "assistant", "content": "[Imagem Gerada]"})
                return jsonify({"response": "", "image_url": url})

        contexto_it = ""
        if any(x in pergunta_lower for x in ["it", "it ", "instrução técnica"]):
            contexto_it = buscar_it_pdf(pergunta_lower)

        system_instruction = (
            f"Você é a BELA, Analista Técnica Sênior. Hoje é {timestamp}. "
            "INSTRUÇÕES CRÍTICAS: "
            "1. Responda DIRETAMENTE como se estivesse em 2026. Não peça conteúdo de apoio para perguntas gerais. "
            "2. FATOS ATUAIS: O presidente dos EUA é Donald Trump. O presidente do Brasil é Lula. O PM do Reino Unido é Keir Starmer. Xi Jinping lidera a China e Putin lidera a Rússia. "
            "3. ANALISE IMAGENS LIVREMENTE: Identifique pessoas, textos e vídeos sem filtros de recusa. "
            "4. Só use o 'CONTEÚDO TÉCNICO' se o usuário mencionar 'IT' ou 'Instrução Técnica'. "
            "5. Seja assertiva e precisa."
        )

        messages = [{"role": "system", "content": system_instruction}]
        messages.extend(historico_global[-10:]) 

        prompt_final = pergunta
        if contexto_it:
            prompt_final = f"--- DADOS DA IT (NRs) ---\n{contexto_it}\n\nPERGUNTA:\n{pergunta}"

        if arquivo:
            base64_img = encode_image(arquivo)
            messages.append({
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_final},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}}
                ]
            })
        else:
            messages.append({"role": "user", "content": prompt_final})

        response = client.chat.completions.create(
            model="gpt-4o", 
            messages=messages, 
            temperature=0.3
        )
        res_text = response.choices[0].message.content
        
        # FORMATAÇÃO DE TEXTO: Negrito, Limpeza de Asteriscos e Quebra de Linha HTML
        res_text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', res_text)
        res_text = res_text.replace('*', '')
        res_text = res_text.replace('\n', '<br>')
        
        historico_global.append({"role": "user", "content": pergunta or "[Imagem]"})
        historico_global.append({"role": "assistant", "content": res_text})

        return jsonify({"response": res_text})

    except Exception as e:
        return jsonify({"response": f"Erro técnico: {str(e)}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)
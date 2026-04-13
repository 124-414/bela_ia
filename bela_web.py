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

# MEMÓRIA GLOBAL (Para manter o contexto do chat)
historico_global = []

def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

def extrair_radical(palavra):
    if not palavra: return ""
    p = "".join(c for c in unicodedata.normalize('NFKD', palavra) if not unicodedata.combining(c))
    p = p.lower().strip()
    return re.sub(r'[^a-z0-9]', '', p)

def buscar_it_pdf(mensagem):
    """Busca técnica nos documentos locais"""
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
        
        # Data e Hora Atual (GMT-4 para exemplo)
        agora = datetime.now(timezone(timedelta(hours=-4)))
        timestamp = agora.strftime('%H:%M de %d/%m/%Y')

        # 1. GERAÇÃO DE IMAGEM (Sem alterar lógica existente)
        gatilhos_criacao = ["imagem", "foto", "gerar", "desenhe", "crie uma imagem"]
        if any(k in pergunta_lower for k in gatilhos_criacao) and not arquivo:
            url = create_image(pergunta)
            if url:
                historico_global.append({"role": "user", "content": pergunta})
                historico_global.append({"role": "assistant", "content": "Imagem gerada com sucesso."})
                return jsonify({"response": "Como sua IA gênio, processei sua solicitação visual. Aqui está:", "image_url": url})

        # 2. BUSCA TÉCNICA (IT)
        contexto_extra = ""
        if any(x in pergunta_lower for x in ["it", "it ", "instrução técnica"]):
            contexto_extra = buscar_it_pdf(pergunta_lower)

        # 3. PROMPT DE SISTEMA (Identidade e Memória)
        system_instruction = (
            f"Você é a BELA, Analista Técnica Sênior de Engenharia e Segurança. "
            f"Hoje é {timestamp}. "
            "Você deve ser precisa, técnica e sempre considerar o histórico da conversa para unificar e-mails ou retomar assuntos. "
            "Se o usuário enviar uma IT, analise com base nas normas de segurança brasileiras (NRs)."
        )

        messages = [{"role": "system", "content": system_instruction}]
        messages.extend(historico_global[-8:]) # Mantém as últimas 8 mensagens na memória

        # 4. TRATAMENTO DE VISÃO OU TEXTO
        if arquivo:
            base64_img = encode_image(arquivo)
            messages.append({
                "role": "user",
                "content": [
                    {"type": "text", "text": f"Analise técnica/OCR: {pergunta}"},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}}
                ]
            })
        else:
            prompt_com_contexto = pergunta
            if contexto_extra:
                prompt_com_contexto = f"CONTEXTO TÉCNICO:\n{contexto_extra}\n\nPERGUNTA:\n{pergunta}"
            messages.append({"role": "user", "content": prompt_com_contexto})

        response = client.chat.completions.create(model="gpt-4o", messages=messages, temperature=0.7)
        res_text = response.choices[0].message.content
        
        # Salva na memória
        historico_global.append({"role": "user", "content": pergunta or "[Imagem Enviada]"})
        historico_global.append({"role": "assistant", "content": res_text})

        return jsonify({"response": res_text})

    except Exception as e:
        return jsonify({"response": f"Erro técnico: {str(e)}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)
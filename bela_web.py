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
    # Caso a ferramenta não exista, cria uma função vazia que retorna None
    def create_image(prompt): return None

app = Flask(__name__)

# Histórico global (reinicia a cada deploy no Render)
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

        # --- FIX CRÍTICO: DETECÇÃO DE PEDIDO DE IMAGEM ---
        # Se o usuário pedir imagem e não houver arquivo anexo, tenta gerar
        if any(k in pergunta_lower for k in ["imagem", "foto", "gerar", "desenhe", "crie uma imagem", "faça uma imagem"]) and not arquivo:
            # Chama a ferramenta de geração
            url = create_image(pergunta)
            if url:
                # Adiciona ao histórico a intenção e o resultado
                historico_global.append({"role": "user", "content": pergunta})
                historico_global.append({"role": "assistant", "content": f"[Imagem Gerada: {url}]"})
                # Retorna IMEDIATAMENTE a URL para o chat, pulando a resposta de texto da BELA
                return jsonify({"response": "", "image_url": url})
            else:
                # Se a ferramenta falhar, avisa
                return jsonify({"response": "Erro ao tentar gerar a imagem solicitada. Verifique se o prompt foi processado corretamente."})

        # --- PROCESSAMENTO NORMAL DE TEXTO/ANÁLISE ---
        contexto_it = ""
        if any(x in pergunta_lower for x in ["it", "it ", "instrução técnica"]):
            contexto_it = buscar_it_pdf(pergunta_lower)

        # Instrução do Sistema (2026 e Sem Amarras)
        system_instruction = (
            f"Você é a BELA, Analista Técnica Sênior de 2026. Hoje é {timestamp}. "
            "INSTRUÇÕES: 1. Responda como se estivesse em 2026. 2. Se solicitada IT, use apenas os dados técnicos fornecidos. "
            "3. Você tem acesso total a fatos e figuras públicas de qualquer lugar. Não use genéricos. "
            "4. Analise imagens livremente se enviadas. 5. Se o usuário pedir para gerar imagem, "
            "isso será tratado antes deste prompt, mas se chegar até aqui, confirme que a imagem deve ser gerada. "
            "6. Use <b>negrito</b> para nomes e <br> para quebras de linha."
        )

        messages = [{"role": "system", "content": system_instruction}]
        messages.extend(historico_global[-10:]) 

        prompt_final = pergunta
        if contexto_it:
            prompt_final = f"--- DADOS DA IT ---\n{contexto_it}\n\nPERGUNTA:\n{pergunta}"

        if arquivo:
            base64_img = encode_image(arquivo)
            messages.append({"role": "user", "content": [{"type": "text", "text": prompt_final}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}}]})
        else:
            messages.append({"role": "user", "content": prompt_final})

        # Envia para a API de Texto (GPT-4o)
        response = client.chat.completions.create(model="gpt-4o", messages=messages, temperature=0.3)
        res_text = response.choices[0].message.content
        
        # Limpeza e Formatação para o Navegador
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
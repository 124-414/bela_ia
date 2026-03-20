import os
import json
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime
import pytz
from tools_google import pesquisar_google

# Inicialização
load_dotenv()
app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# MEMÓRIA DE SESSÃO (Essencial para o Render manter o histórico vivo)
MEMORIA_GLOBAL = []

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    global MEMORIA_GLOBAL
    data = request.get_json()
    user_message = data.get("message", "").strip()
    
    if not user_message:
        return jsonify({"response": "BELA pronta para análise."})

    fuso_bsb = pytz.timezone('America/Sao_Paulo')
    data_hoje = datetime.now(fuso_bsb).strftime('%d/%m/%Y')

    # 1. BUSCA WEB (Mantendo a precisão que você validou)
    try:
        contexto_web = pesquisar_google(user_message)
    except:
        contexto_web = "Web indisponível no momento."

    try:
        # 2. PROMPT DE CHOQUE (Anti-Tutorial e Anti-Amnésia)
        prompt_sistema = (
            f"Você é a BELA, IA Analítica de 2026. Hoje é {data_hoje}.\n\n"
            "DIRETRIZES CRÍTICAS:\n"
            "1. NÃO DÊ DICAS: Se o usuário pedir para 'melhorar', 'ajustar' ou 'acrescentar', NÃO explique como fazer. Escreva o novo texto completo e robusto IMEDIATAMENTE.\n"
            "2. CONEXÃO TOTAL: Você deve obrigatoriamente usar as mensagens anteriores para manter o contexto. Se o assunto era Rússia, a melhoria é sobre a Rússia.\n"
            "3. PROIBIDO COLCHETES: Nunca use [Nome], [Cargo] ou [Data]. Preencha os fatos ou deixe o espaço limpo para assinatura natural.\n"
            "4. ESTILO: E-mails fluidos, robustos e profissionais. Proibido tabelas e listas de tutoriais.\n\n"
            f"DADOS ATUAIS DA WEB: {contexto_web}"
        )

        # 3. Montagem do Histórico para a API (Onde ela 'enxerga' o passado)
        mensagens_ia = [{"role": "system", "content": prompt_sistema}]
        
        # Injeta o histórico da sessão (Últimas 10 mensagens)
        for m in MEMORIA_GLOBAL[-10:]:
            mensagens_ia.append(m)
            
        mensagens_ia.append({"role": "user", "content": user_message})

        # 4. Chamada da Inteligência (Temperatura baixa = mais foco)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=mensagens_ia,
            temperature=0.2 
        )
        
        resposta_final = response.choices[0].message.content

        # 5. ATUALIZAÇÃO DA MEMÓRIA
        MEMORIA_GLOBAL.append({"role": "user", "content": user_message})
        MEMORIA_GLOBAL.append({"role": "assistant", "content": resposta_final})

        # Mantém a memória limpa (apenas as últimas 20 mensagens para performance)
        MEMORIA_GLOBAL = MEMORIA_GLOBAL[-20:]

        return jsonify({"response": resposta_final})

    except Exception as e:
        return jsonify({"response": f"Erro analítico: {str(e)}"})

if __name__ == "__main__":
    # Porta dinâmica para o Render (ele usa a variável de ambiente PORT)
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
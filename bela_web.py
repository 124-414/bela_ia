import os
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime, timezone, timedelta
import pytz
from tools_google import pesquisar_google

load_dotenv()
app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "").strip()
    
    if not user_message:
        return jsonify({"response": "Como posso ajudar você hoje?"})

    # --- MOTOR DE TEMPO UNIVERSAL (UTC) ---
    # Usamos o UTC como base para calcular qualquer lugar do mundo sem erros
    agora_utc = datetime.now(timezone.utc)
    data_hoje = agora_utc.strftime('%d/%m/%Y')
    
    # 1. BUSCA WEB ATIVA (Para fatos, política e eventos globais)
    contexto_web = pesquisar_google(user_message)
    
    try:
        # PROMPT DE CONTEXTO GERAL E ATUALIZADO
        prompt_sistema = (
            f"Você é a Bela, uma assistente virtual avançada operando em {data_hoje}.\n"
            f"REFERÊNCIA MUNDIAL: O horário atual em UTC-0 é {agora_utc.strftime('%H:%M')}.\n\n"
            "DIRETRIZES DE PENSAMENTO:\n"
            "1. CONTEXTO GLOBAL: Você deve ser capaz de informar sobre qualquer país, estado ou cidade.\n"
            "2. REALIDADE 2026: Trump é o presidente dos EUA (desde 2025), Lula é o presidente do Brasil, "
            "Milei na Argentina, Macron na França. Use os dados da web para outros líderes.\n"
            "3. LÓGICA DE FUSO: Ao responder sobre horários, verifique o desvio UTC da região. "
            "Exemplo: Brasília (UTC-3), Mato Grosso/Rondônia/Bolívia (UTC-4), Portugal (UTC+1).\n"
            "4. BUSCA WEB: Priorize sempre as informações retornadas abaixo. Se a busca falhar, "
            "use seu conhecimento geral atualizado para 2026.\n"
            "5. PRECISÃO: Não invente fatos. Se não houver registro de um evento em 2026, informe que não encontrou.\n"
            f"\nDADOS DA WEB (TEMPO REAL): {contexto_web if contexto_web else 'Sem notícias recentes. Use lógica de 2026.'}"
        )

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": prompt_sistema},
                {"role": "user", "content": user_message}
            ],
            temperature=0.2 # Equilíbrio entre precisão e fluidez na conversa
        )
        
        resposta = response.choices[0].message.content
        return jsonify({"response": resposta})

    except Exception as e:
        print(f"Erro OpenAI: {e}")
        return jsonify({"response": "Desculpe, tive um problema ao processar sua pergunta."})

if __name__ == "__main__":
    # Mantemos debug=True para facilitar seus testes locais
    app.run(host="127.0.0.1", port=8080, debug=True)
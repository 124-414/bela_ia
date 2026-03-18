@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")

    print("Mensagem recebida:", user_message)

    # ⏰ Hora
    brasilia = pytz.timezone("America/Sao_Paulo")
    agora = datetime.now(brasilia)
    hora = agora.strftime("%d/%m/%Y %H:%M:%S")

    # 🔎 detectar se deve buscar notícias
    palavras = ["notícia", "noticias", "guerra", "hoje", "atual", "acontecendo"]

    artigos = []
    if any(p in user_message.lower() for p in palavras):
        artigos = buscar_noticias(user_message)

    # 🧠 contexto equilibrado
    contexto = f"Data atual: {hora}\n"

    if artigos:
        contexto += "\nNotícias recentes:\n"
        for art in artigos:
            contexto += f"- {art.get('title')} ({art.get('source', {}).get('name')})\n"
            contexto += f"{art.get('url')}\n\n"

    try:
        resposta = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """Você é a Bela, uma IA inteligente e confiável.

REGRAS:
- Responda normalmente usando conhecimento geral.
- Se houver notícias, use como complemento.
- NÃO invente fatos.
- NÃO diga que não tem acesso à internet.
- Seja direta, clara e útil."""
                },
                {
                    "role": "user",
                    "content": contexto + "\nPergunta: " + user_message
                }
            ],
            timeout=10
        )

        texto = resposta.choices[0].message.content

    except Exception as e:
        print("Erro OpenAI:", e)
        texto = "Estou com instabilidade no momento. Tente novamente."

    return jsonify({"response": texto})
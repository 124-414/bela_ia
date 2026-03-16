@app.route("/chat", methods=["POST"])
def chat():

    data = request.json
    user_message = data.get("message")

    data_atual = datetime.now().strftime("%d/%m/%Y")
    hora_atual = datetime.now().strftime("%H:%M")

    memoria.append({
        "role": "user",
        "content": user_message
    })

    resposta = client.responses.create(
        model="gpt-4.1-mini",
        tools=[{"type": "web_search_preview"}],
        input=[
            {
                "role": "system",
                "content": f"""
Você é a Bela IA.

Data atual: {data_atual}
Hora atual: {hora_atual}

Responda sempre em português.
"""
            }
        ] + memoria
    )

    reply = resposta.output_text

    memoria.append({
        "role": "assistant",
        "content": reply
    })

    return jsonify({"response": reply})
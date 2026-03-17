async function send() {
    const input = document.getElementById("input");
    const chat = document.getElementById("chat");
    const button = document.getElementById("send");

    const message = input.value.trim();
    if (!message) return;

    // Desativa botão enquanto envia
    button.disabled = true;

    // Mostra mensagem do usuário
    chat.innerHTML += `<p class="user"><b>Você:</b> ${message}</p>`;

    // Scroll automático
    chat.scrollTop = chat.scrollHeight;

    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ message: message })
        });

        if (!response.ok) {
            throw new Error("Erro na requisição: " + response.status);
        }

        const data = await response.json();

        chat.innerHTML += `<p class="bot"><b>Bela:</b> ${data.response}</p>`;

    } catch (error) {
        console.error("Erro:", error);
        chat.innerHTML += `<p class="bot"><b>Bela:</b> Erro ao conectar com o servidor.</p>`;
    }

    // Limpa input
    input.value = "";

    // Reativa botão
    button.disabled = false;

    // Scroll automático
    chat.scrollTop = chat.scrollHeight;
}


// Permitir enviar com ENTER
document.getElementById("input").addEventListener("keypress", function (e) {
    if (e.key === "Enter") {
        send();
    }
});

// Botão enviar
document.getElementById("send").addEventListener("click", send);
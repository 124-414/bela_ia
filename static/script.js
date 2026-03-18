async function send() {
    const input = document.getElementById("input");
    const chat = document.getElementById("chat");
    const button = document.getElementById("send");

    const message = input.value.trim();
    if (!message) return;

    // Desativa botão enquanto envia
    button.disabled = true;

    // Mostra mensagem do usuário
    chat.innerHTML += `
        <div class="user">
            <img src="https://via.placeholder.com/40" alt="User"/>
            <div class="message">${message}</div>
        </div>
    `;

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

        chat.innerHTML += `
            <div class="bot">
                <img src="https://via.placeholder.com/40" alt="Bot"/>
                <div class="message">${data.response}</div>
            </div>
        `;

    } catch (error) {
        console.error("Erro:", error);
        chat.innerHTML += `
            <div class="bot">
                <img src="https://via.placeholder.com/40" alt="Bot"/>
                <div class="message">Erro ao conectar com o servidor.</div>
            </div>
        `;
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
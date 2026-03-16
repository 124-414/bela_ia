const input = document.getElementById("input");
const messages = document.getElementById("messages");
const sendBtn = document.getElementById("send");
const micBtn = document.getElementById("mic");

function sendMessage() {

    const texto = input.value.trim();
    if (!texto) return;

    // Mensagem do usuário
    messages.innerHTML += `
        <div class="linha user">
            <div class="bolha">${texto}</div>
        </div>
    `;

    messages.scrollTop = messages.scrollHeight;
    input.value = "";

    fetch("/perguntar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: texto })
    })
    .then(res => res.json())
    .then(data => {

        messages.innerHTML += `
            <div class="linha bot">
                <div class="bolha">${data.resposta}</div>
            </div>
        `;

        messages.scrollTop = messages.scrollHeight;
    });
}

// BOTÃO
sendBtn.addEventListener("click", sendMessage);

// ENTER
input.addEventListener("keydown", function(e) {
    if (e.key === "Enter") {
        sendMessage();
    }
});

// MICROFONE
micBtn.addEventListener("click", function() {

    if (!('webkitSpeechRecognition' in window)) {
        alert("Seu navegador não suporta microfone.");
        return;
    }

    const recognition = new webkitSpeechRecognition();
    recognition.lang = "pt-BR";

    recognition.start();

    recognition.onresult = function(event) {
        input.value = event.results[0][0].transcript;
    };
});
const chat = document.getElementById("chat");
const input = document.getElementById("input");
const send = document.getElementById("send");

function addMessage(text, className) {
    const div = document.createElement("div");
    div.className = className;
    div.innerHTML = text;
    chat.appendChild(div);
    chat.scrollTop = chat.scrollHeight;
}

send.onclick = async () => {
    const message = input.value;
    if (!message) return;

    addMessage("Você: " + message, "user");
    input.value = "";

    try {
        const res = await fetch("/chat", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({message})
        });

        const data = await res.json();

        addMessage("Bela: " + data.response, "bot");

    } catch (err) {
        addMessage("Erro de conexão com servidor.", "bot");
    }
};
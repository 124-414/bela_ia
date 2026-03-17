async function send() {
    const input = document.getElementById("input");
    const chat = document.getElementById("chat");

    const message = input.value;
    if (!message) return;

    chat.innerHTML += "<p><b>Você:</b> " + message + "</p>";

    const response = await fetch("/chat", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({message: message})
    });

    const data = await response.json();

    chat.innerHTML += "<p><b>Bela:</b> " + data.response + "</p>";

    input.value = "";
}
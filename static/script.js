const input = document.getElementById("input");
const chat = document.getElementById("chat");
const sendBtn = document.getElementById("send");

async function send(){

let msg = input.value.trim();
if(!msg) return;

chat.innerHTML += `<div class="user">Você: ${msg}</div>`;
input.value="";

let res = await fetch("/chat",{
method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({message:msg})
});

let data = await res.json();

chat.innerHTML += `<div class="bot">Bela: ${data.response}</div>`;

chat.scrollTop = chat.scrollHeight;
}

sendBtn.addEventListener("click", send);

input.addEventListener("keypress", function(e){
if(e.key==="Enter") send();
});
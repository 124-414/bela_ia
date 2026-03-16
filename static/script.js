const input = document.getElementById("input");
const chat = document.getElementById("chat");
const sendBtn = document.getElementById("send");
const micBtn = document.getElementById("mic");

async function send(){

let msg = input.value.trim();
if(!msg) return;

chat.innerHTML += `<div class="user">Você: ${msg}</div>`;
input.value="";

try{

let res = await fetch("/chat",{
method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({message:msg})
});

let data = await res.json();

chat.innerHTML += `<div class="bot">Bela: ${data.response}</div>`;

speak(data.response);

}catch{

chat.innerHTML += `<div class="bot">Erro de conexão.</div>`;

}

chat.scrollTop = chat.scrollHeight;
}

sendBtn.addEventListener("click", send);

input.addEventListener("keypress", function(e){
if(e.key==="Enter") send();
});

// VOZ (texto → fala)
function speak(text){
let utterance = new SpeechSynthesisUtterance(text);
utterance.lang = "pt-BR";
speechSynthesis.speak(utterance);
}

// MICROFONE
micBtn.addEventListener("click", function(){

if(!('webkitSpeechRecognition' in window)){
alert("Seu navegador não suporta voz.");
return;
}

const recognition = new webkitSpeechRecognition();
recognition.lang="pt-BR";
recognition.start();

recognition.onresult=function(event){
input.value = event.results[0][0].transcript;
};

});
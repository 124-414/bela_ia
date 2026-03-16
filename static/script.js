const input = document.getElementById("input");
const messages = document.getElementById("messages");

function enviar(){

const texto = input.value.trim();
if(!texto) return;

messages.innerHTML += `
<div class="linha user">
<div class="bolha">${texto}</div>
</div>
`;

messages.scrollTop = messages.scrollHeight;

input.value = "";

fetch("/perguntar",{
method:"POST",
headers:{
"Content-Type":"application/json"
},
body:JSON.stringify({
message:texto
})
})
.then(res=>res.json())
.then(data=>{

messages.innerHTML += `
<div class="linha bot">

<img class="avatar" src="/static/bela.png">

<div class="bolha bot">${data.resposta}</div>

</div>
`;

messages.scrollTop = messages.scrollHeight;

});

}

input.addEventListener("keypress",function(e){
if(e.key==="Enter"){
enviar();
}
});
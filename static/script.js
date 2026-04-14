<script>
    var currentFile = null;

    // 1. Capturar Colar (Paste)
    document.addEventListener('paste', function(e) {
        var items = e.clipboardData.items;
        for (var i = 0; i < items.length; i++) {
            if (items[i].type.indexOf("image") !== -1) {
                var file = items[i].getAsFile();
                showPreview(file);
            }
        }
    });

    // 2. Pré-visualização
    function showPreview(file) {
        currentFile = file;
        var reader = new FileReader();
        reader.onload = function(e) {
            document.getElementById('preview-img').src = e.target.result;
            document.getElementById('preview-area').style.display = 'flex';
        };
        reader.readAsDataURL(file);
    }

    function clearPreview() {
        currentFile = null;
        document.getElementById('preview-area').style.display = 'none';
    }

    function handleFileSelect(e) {
        if (e.target.files[0]) showPreview(e.target.files[0]);
    }

    // 3. Enviar Mensagem
    async function sendMessage() {
        var input = document.getElementById('user-input');
        var chat = document.getElementById('chat');
        var message = input.value.trim();
        var file = currentFile;

        if (!message && !file) return;

        // Adiciona balão do utilizador
        var userDiv = document.createElement('div');
        userDiv.className = 'msg user';
        userDiv.innerHTML = message;
        if (file) {
            var img = document.createElement('img');
            img.src = document.getElementById('preview-img').src;
            img.className = 'chat-img';
            userDiv.appendChild(document.createElement('br'));
            userDiv.appendChild(img);
        }
        chat.appendChild(userDiv);

        input.value = '';
        clearPreview();
        document.getElementById('typing').style.display = 'block';
        chat.scrollTop = chat.scrollHeight;

        var formData = new FormData();
        formData.append('message', message);
        if (file) formData.append('file', file);

        try {
            var response = await fetch('/chat', { method: 'POST', body: formData });
            var data = await response.json();
            document.getElementById('typing').style.display = 'none';

            var botDiv = document.createElement('div');
            botDiv.className = 'msg bot';
            
            var botHtml = '<span class="bot-tag">BELA</span>' +
                          '<button class="btn-copy-top" onclick="copyContent(this)">📄 Copiar</button>' +
                          '<div class="bot-text">' + data.response + '</div>';
            
            if (data.image_url) {
                botHtml += '<br><img src="' + data.image_url + '" class="chat-img">' +
                           '<br><button class="btn-copy-top" style="position:relative; top:0; right:0;" onclick="window.open(\'' + data.image_url + '\', \'_blank\')">🔍 Ver Original</button>';
            }
            
            botDiv.innerHTML = botHtml;
            chat.appendChild(botDiv);
        } catch (e) {
            document.getElementById('typing').style.display = 'none';
            chat.innerHTML += '<div class="msg bot">Erro técnico ao processar.</div>';
        }
        chat.scrollTop = chat.scrollHeight;
    }

    // 4. FUNÇÃO COPIAR (VERSÃO ULTRA-ESTÁVEL)
    function copyContent(btn) {
        try {
            var pai = btn.parentElement;
            var textoDiv = pai.querySelector('.bot-text');
            var textoParaCopiar = textoDiv.innerText;

            var x = document.createElement("textarea");
            x.value = textoParaCopiar;
            document.body.appendChild(x);
            x.select();
            document.execCommand("copy");
            document.body.removeChild(x);

            var textoOriginal = btn.innerHTML;
            btn.innerHTML = "✅!";
            setTimeout(function() { btn.innerHTML = textoOriginal; }, 1500);
        } catch (err) {
            console.log("Erro ao copiar");
        }
    }
</script>
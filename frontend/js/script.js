let chatHistory = [];

async function enviar(inputValue) {
  const input = inputValue?.trim() || $('#input').val().trim();
  if (!input) return;

  const $resposta = $('#resposta');

  // Append user message immediately
  $resposta.append(`<div class="chat-bubble-sent">${input}</div>`);
  $('#resposta').scrollTop($('#resposta')[0].scrollHeight);
  $('#input').val("").focus();

  // Append loading bubble
  let typingHtml = '<span class="dot"></span><span class="dot"></span><span class="dot"></span>';
  const loadingBubble = $(`<div class="chat-bubble-received">${typingHtml}</div>`);
  $resposta.append(loadingBubble);
  $('#resposta').scrollTop($('#resposta')[0].scrollHeight);

  // push no array: msg user
  chatHistory.push({ role: "user", content: input });

  // termos para não destacar
  const forbiddenTerms = ["bip", "bip bop", "bip-bop", "beep-bop", "dica", "beep", "bip-bop!"];

  const modeloSelecionado = $('#modelo').val();

  try {
    const res = await fetch("http://localhost:5000/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: input, history: chatHistory, model: modeloSelecionado })
    });

    const data = await res.json();
    console.log("Resposta da API:", data); // <---- veja isso no console
    const resposta = data.choices?.[0]?.message?.content || "Erro na resposta: sem conteúdo";

    //arr push: bot msg
    chatHistory.push({ role: "assistant", content: resposta });
    
    if (chatHistory.length > 6) {
      chatHistory = chatHistory.slice(-6);
    }

    // regex to replace *asteriscs* with span tag
    const formattedResponse = resposta.replace(/\*(.*?)\*/g, (match, p1) => {
      
      // remover destaque dos termos da blacklist do robo (forbiddenTerms)
      if (forbiddenTerms.includes(p1.toLowerCase())) {
        return match; // Retorna o termo original sem mudanças
      }

      return `<span class="highlight-term" onclick="gerarInput('${p1}')">${p1}</span>`;
    });

    // Replace loading with response
    loadingBubble.replaceWith(`<div class="chat-bubble-received">${formattedResponse}</div>`);
    $('#resposta').scrollTop($('#resposta')[0].scrollHeight);
  } catch (error) {
    loadingBubble.replaceWith(`<div class="chat-bubble-received">Erro na conexão com o Edinho 🤖💥</div>`);
    $('#resposta').scrollTop($('#resposta')[0].scrollHeight);
    console.error("Erro:", error);
  }

  // Enable input again
  isSending = false;
  $('#input').prop('disabled', false);
  $('#input').val("").focus();

}

// the highlighted terms call this function
function gerarInput(term){
  $("#input").val("Quero saber mais sobre: " + term);
  $("#input").focus();
}

// images
const avatarImages = [
  "pix/avatar/roboedinho1.png",
  "pix/avatar/roboedinho2.png",
  "pix/avatar/roboedinho3.png",
  "pix/avatar/roboedinho4.png",
  "pix/avatar/roboedinho5.png",
  "pix/avatar/roboedinho6.png",
  "pix/avatar/roboedinho7.png",
  "pix/avatar/roboedinho8.png",
];

let currentAvatarIndex = 0;
let isSending = false;

$(document).ready(function () {

  // Change avatar on click
  $("#next-avatar").on("click", function () {
    currentAvatarIndex = (currentAvatarIndex + 1) % avatarImages.length;
    const nextImage = avatarImages[currentAvatarIndex];
    $("#avatar-ed").css("background-image", `url('${nextImage}')`);
  });

  // Send message oin ENter
  $('#input').on('keydown', function (e) {
    if (e.key === 'Enter') {
      e.preventDefault();
      const inputVal = $(this).val().trim();

      // Avoiding spam (or trying lol)
      if (inputVal.length > 0 && !isSending) {
        isSending = true;
        $(this).prop('disabled', true); //disable input field

        // Call send message
        enviar(inputVal);        
      }
    }
  });


});

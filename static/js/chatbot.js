const messages = document.querySelector("#messages");
const welcomeScreen = document.querySelector(".welcome-screen");
const input = document.querySelector("#chat-input");
const form = document.querySelector("#chat-form");
const sendButton = form.querySelector("button[type='submit']");
const suggestions = document.querySelectorAll(".suggestion-btn");
const clearForm = document.querySelector("#clear-form");
const backButton = document.querySelector("#back-button");
const overlay = document.querySelector("#circleOverlay");
const root = document.documentElement;

function maxRadiusFrom(x, y){
  const vw = window.innerWidth, vh = window.innerHeight;
  const dx = Math.max(x, vw - x);
  const dy = Math.max(y, vh - y);
  return Math.hypot(dx, dy);
}

(function playEntranceIfNeeded(){
  const phase = sessionStorage.getItem('foxTransitionPhase');
  if (phase !== 'toChat') return;

  requestAnimationFrame(() => {
    overlay.classList.remove('no-transition');
    requestAnimationFrame(() => {
      root.style.setProperty('--r', '0px');
    });
  });

  sessionStorage.removeItem('foxTransitionPhase');
})();

backButton.addEventListener("click", () => {
  const x = parseFloat(sessionStorage.getItem('foxOriginX'));
  const y = parseFloat(sessionStorage.getItem('foxOriginY'));

  // gak ada origin tersimpen (misal chatbot dibuka langsung lewat URL)
  // -> gak ada yang di-reverse, langsung pindah biasa
  if (Number.isNaN(x) || Number.isNaN(y)){
    window.location.href = "/";
    return;
  }

  root.style.setProperty('--ox', x + 'px');
  root.style.setProperty('--oy', y + 'px');
  overlay.classList.remove('no-transition');
  root.style.setProperty('--r', maxRadiusFrom(x, y) + 'px');

  sessionStorage.setItem('foxTransitionPhase', 'toHome');

  overlay.addEventListener('transitionend', function onEnd(e){
    if (e.propertyName !== 'clip-path') return;
    overlay.removeEventListener('transitionend', onEnd);
    window.location.href = "/";
  });
});

suggestions.forEach((button)=>{
  button.addEventListener("click", ()=>{
    const pesan = button.textContent.trim();
      kirimPesan(pesan);
  });
});

function updateSendButton(){
  const isEmpty = input.value.trim() === "";
  sendButton.disabled = isEmpty || sendButton.dataset.sending === "true";
}

function setSending(isSending){
  sendButton.dataset.sending = isSending;
  input.disabled = isSending;
  suggestions.forEach((button) => button.disabled = isSending);
  clearButton.disabled = isSending || messages.children.length === 0;
  updateSendButton();
}

input.addEventListener("input", updateSendButton);
updateSendButton();

function kirimPesan(pesan){
  welcomeScreen.style.display = "none";
  buatBubble("Rio", pesan);
  input.value = "";
  setSending(true);
  const typing = tampilkanTyping();
  fetch("/api/chat", {
      method: "POST",
      body: new URLSearchParams({
      pesan: pesan
    })
  })
    .then((response) => response.json().then((data) => ({ response, data })))
    .then(({ response, data }) => {
      typing.remove()
      if (!response.ok) {
        buatBubble("AI", data.error || "Terjadi kesalahan. Coba lagi.");
        return;
      }
      buatBubble("AI", data.reply);
    })
    .catch((error) => {
      typing.remove();
      console.error(error);
    })
    .finally(() => {
      setSending(false);
    });
}

form.addEventListener("submit", (event) => {
    event.preventDefault();
    const pesan = input.value.trim();
    if (pesan === "") {
    return;
    }
    kirimPesan(pesan);
    console.log(pesan);
    });

const clearButton = document.querySelector("#clear-button");

function updateClearButton(){
  clearButton.disabled = messages.children.length === 0;
}

clearForm.addEventListener("submit", (event) => {
  event.preventDefault();
  fetch("/clear", { method: "POST" })
    .then(() => {
      messages.innerHTML = "";
      welcomeScreen.style.display = "";
      input.value = "";
      setSending(false);
      updateClearButton();
    })
    .catch((error) => console.error(error));
});

function buatBubble(sender, text){
  const bubble = document.createElement("div");
  bubble.className = "message " + sender;
  bubble.textContent = text;
  messages.appendChild(bubble);

  updateClearButton();
  scrollkebawah();
  }

if(messages.children.length > 0){
  welcomeScreen.style.display = "none";
}
updateClearButton();

function tampilkanTyping(){
  const typing = document.createElement("div");
  typing.className = "typing-wrapper";
  typing.innerHTML = `
    <div class="typing-loader" role="status" aria-live="polite" aria-label="Chatbot sedang mengetik">
    <div class="orbs" aria-hidden="true">
      <span class="orb"></span>
      <span class="orb"></span>
      <span class="orb"></span>
    </div>
    <span class="label">Thinking...</span>
  </div>
  `;
  messages.appendChild(typing);
  scrollkebawah();
  return typing;
}

function scrollkebawah(){
  const chatHistory = document.querySelector(".chat-history");

  requestAnimationFrame(() => {
    chatHistory.scrollTo({
      top: chatHistory.scrollHeight,
      behavior: "smooth"
    });
  });
}
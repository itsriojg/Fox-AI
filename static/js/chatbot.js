const messages = document.querySelector("#messages");
const welcomeScreen = document.querySelector(".welcome-screen");
const input = document.querySelector("#chat-input");
const form = document.querySelector("#chat-form");
const sendButton = form.querySelector("button[type='submit']");
const suggestions = document.querySelectorAll(".suggestion-btn");
const clearForm = document.querySelector("#clear-form");
const clearButton = document.querySelector("#clear-button");
const backButton = document.querySelector("#back-button");
const overlay = document.querySelector("#circleOverlay");
const root = document.documentElement;

window.onunload = () => {};

root.style.setProperty('--r', '0px');

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

function handleBackNavigation() {
  const x = parseFloat(sessionStorage.getItem('foxOriginX'));
  const y = parseFloat(sessionStorage.getItem('foxOriginY'));

  if (Number.isNaN(x) || Number.isNaN(y)) {
    window.location.href = "/";
    return;
  }

  if (backButton.dataset.leaving) return;

  backButton.dataset.leaving = "true";

  overlay.classList.add('no-transition');
  root.style.setProperty('--ox', x + 'px');
  root.style.setProperty('--oy', y + 'px');

  overlay.getBoundingClientRect();

  overlay.classList.remove('no-transition');

  requestAnimationFrame(() => {
    root.style.setProperty('--r', maxRadiusFrom(x, y) + 'px');
  });

  sessionStorage.setItem('foxTransitionPhase', 'toHome');

  function onEnd(e) {
    if (e.propertyName !== 'clip-path') return
    goHome()
  }

  overlay.addEventListener('transitionend', onEnd)

  let done = false;
  let cleanupDone = false;
  let fallbackTimer = null;

  const cleanup = () => {
    if (cleanupDone) return;
    cleanupDone = true;
    overlay.removeEventListener('transitionend', onEnd);
    if (fallbackTimer) clearTimeout(fallbackTimer);
  };

  const goHome = () => {
    if (done) return;
    done = true;
    cleanup();
    history.replaceState(null, '', '/');
    window.location.href = "/";
  };

  // Navigate pas 70% animasi (630ms dari 900ms)
  // Supaya loading bar ketutupan overlay
  fallbackTimer = setTimeout(goHome, 630);
}

backButton.addEventListener("click", handleBackNavigation);

// Handle mobile back button via beforeunload
window.addEventListener('beforeunload', () => {
  // Jika page unloading karena back button, set flag
  // Note: tidak bisa detect pasti back button vs other navigation
  if (!sessionStorage.getItem('foxTransitionPhase')) {
    sessionStorage.setItem('foxBackNavigation', 'true');
  }
});

// Fallback: pageshow untuk BFCache scenario
window.addEventListener('pageshow', (event) => {
  if (event.persisted && sessionStorage.getItem('foxTransitionPhase') === 'toChat') {
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
  }
});

// Mencegah blackscreen jika browser restore /chatbot dari BFCache
window.addEventListener('pageshow', (event) => {
  if (event.persisted && !sessionStorage.getItem('foxTransitionPhase')) {
    window.location.href = '/';
  }
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
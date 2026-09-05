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

function safeGet(key){ try{ return sessionStorage.getItem(key); }catch(e){ return null; } }
function safeSet(key,val){ try{ sessionStorage.setItem(key,val); }catch(e){} }
function safeRemove(key){ try{ sessionStorage.removeItem(key); }catch(e){} }

const splash = document.getElementById('mintifSplash');
const splashImg = splash ? splash.querySelector('img') : null;
let splashTimers = [];
let splashDone = false;

function shouldShowSplash(isToChat){
  if (!splash || !splashImg) return false;
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return false;
  if (messages.children.length > 0) return false;
  if (welcomeScreen && getComputedStyle(welcomeScreen).display === 'none') return false;
  return isToChat;
}
function revealWelcome(){
  document.body.classList.add('welcome-ready');
  if (splash) {
    splash.style.display = 'none';
    splash.classList.remove('is-active','is-out');
    if (splashImg) {
      splashImg.style.transition = 'none';
      splashImg.style.transform = 'none';
    }
  }
}
function clearSplashTimers(){
  splashTimers.forEach(clearTimeout);
  splashTimers = [];
}
function flipToWelcome(doneCb){
  const target = document.querySelector('.mintif-logo img');
  if (!target || !splashImg) {
    if (doneCb) doneCb();
    return;
  }
  const sRect = splashImg.getBoundingClientRect();
  const tRect = target.getBoundingClientRect();
  const sCx = sRect.left + sRect.width / 2;
  const sCy = sRect.top + sRect.height / 2;
  const tCx = tRect.left + tRect.width / 2;
  const tCy = tRect.top + tRect.height / 2;
  const dx = tCx - sCx;
  const dy = tCy - sCy;
  const scale = tRect.width / sRect.width;
  splashImg.style.transition = 'transform .4s cubic-bezier(.65, 0, .35, 1)';
  splashImg.getBoundingClientRect();
  splashImg.style.transform = `translate(${dx}px, ${dy}px) scale(${scale})`;
  let finished = false;
  const finish = () => {
    if (finished) return;
    finished = true;
    splashImg.removeEventListener('transitionend', onEnd);
    splash.style.display = 'none';
    splash.classList.remove('is-out');
    splashImg.style.transition = 'none';
    splashImg.style.transform = 'none';
    document.body.classList.add('welcome-ready','splash-done');
    if (doneCb) doneCb();
  };
  function onEnd(e){
    if (e.propertyName !== 'transform') return;
    finish();
  }
  splashImg.addEventListener('transitionend', onEnd);
  const fallback = setTimeout(finish, 500);
  splashTimers.push(fallback);
}
function playMintifSplash(){
  if (!splash || !splashImg || splashDone) return;
  splashDone = true;
  splash.style.display = 'grid';
  splashImg.style.transition = 'none';
  splashImg.style.transform = 'none';
  splash.getBoundingClientRect();
  requestAnimationFrame(() => splash.classList.add('is-active'));
  const tHold = setTimeout(() => {
    splash.classList.remove('is-active');
    splash.classList.add('is-out');
    flipToWelcome();
  }, 900);
  splashTimers.push(tHold);
  const skip = () => {
    clearSplashTimers();
    splash.classList.remove('is-active');
    splash.classList.add('is-out');
    // langsung FLIP tanpa tunggu hold
    requestAnimationFrame(() => flipToWelcome());
  };
  splash.addEventListener('click', skip, { once: true });
}

// hanya reset ke 0 kalau bukan arrival dari home (toChat)
// kalau toChat, --r sudah di-set max di inline script chatbot.html biar overlay ketutup sebelum paint
const _isToChatArrival = safeGet('foxTransitionPhase') === 'toChat';
if (!_isToChatArrival) {
  root.style.setProperty('--r', '0px');
  overlay.style.removeProperty('--r');
  revealWelcome();
}

function maxRadiusFrom(x, y){
  const vw = window.innerWidth, vh = window.innerHeight;
  const dx = Math.max(x, vw - x);
  const dy = Math.max(y, vh - y);
  return Math.hypot(dx, dy);
}

(function playEntranceIfNeeded(){
  if (!_isToChatArrival) return;

  const needsSplash = shouldShowSplash(true);

  overlay.style.removeProperty('--r');
  requestAnimationFrame(() => {
    overlay.classList.remove('no-transition');
    overlay.getBoundingClientRect();
    requestAnimationFrame(() => {
      root.style.setProperty('--r', '0px');
      if (needsSplash) {
        // overlap 180ms biar circle udah kebuka 20% baru logo mulai, zoom 0.08→1 jadi keliatan
        const t = setTimeout(playMintifSplash, 180);
        splashTimers.push(t);
      }
    });
  });

  safeRemove('foxTransitionPhase');

  if (!needsSplash) {
    // tanpa splash, reveal setelah circle selesai (0.65s) biar welcome tidak flash
    let revealed = false;
    const doReveal = () => {
      if (revealed) return;
      revealed = true;
      overlay.removeEventListener('transitionend', onEnd);
      revealWelcome();
    };
    function onEnd(e){
      if (e.propertyName !== 'clip-path') return;
      doReveal();
    }
    overlay.addEventListener('transitionend', onEnd);
    const fb = setTimeout(doReveal, 700);
    splashTimers.push(fb);
  }
})();

function handleBackNavigation() {
  const x = parseFloat(safeGet('foxOriginX'));
  const y = parseFloat(safeGet('foxOriginY'));

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

  safeSet('foxTransitionPhase', 'toHome');

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
    try{ history.replaceState(null, '', '/'); }catch(e){}
    window.location.href = "/";
  };

  // Navigate pas 70% animasi (455ms dari 650ms)
  // Supaya loading bar ketutupan overlay
  fallbackTimer = setTimeout(goHome, 455);
}

backButton.addEventListener("click", handleBackNavigation);

// Handle mobile back button via pagehide (lebih aman dari beforeunload untuk BFCache)
window.addEventListener('pagehide', () => {
  if (!safeGet('foxTransitionPhase')) {
    safeSet('foxBackNavigation', 'true');
  }
});

// Fallback: pageshow untuk BFCache scenario
window.addEventListener('pageshow', (event) => {
  if (event.persisted && safeGet('foxTransitionPhase') === 'toChat') {
    const needsSplash = shouldShowSplash(true);
    overlay.style.removeProperty('--r');
    requestAnimationFrame(() => {
      overlay.classList.remove('no-transition');
      overlay.getBoundingClientRect();
      requestAnimationFrame(() => {
        root.style.setProperty('--r', '0px');
        if (needsSplash) {
          const t = setTimeout(playMintifSplash, 180);
          splashTimers.push(t);
        }
      });
    });
    safeRemove('foxTransitionPhase');
    if (!needsSplash) {
      let revealed = false;
      const doReveal = () => {
        if (revealed) return;
        revealed = true;
        overlay.removeEventListener('transitionend', onEnd);
        revealWelcome();
      };
      function onEnd(e){
        if (e.propertyName !== 'clip-path') return;
        doReveal();
      }
      overlay.addEventListener('transitionend', onEnd);
      const fb = setTimeout(doReveal, 700);
      splashTimers.push(fb);
    }
  } else if (event.persisted && !safeGet('foxTransitionPhase')) {
    // BFCache restore normal — jangan paksa redirect ke '/', cukup reveal welcome
    // biar ga blackscreen (fix: sebelumnya window.location.href='/' bikin loop)
    root.style.setProperty('--r', '0px');
    overlay.style.removeProperty('--r');
    overlay.classList.remove('no-transition');
    revealWelcome();
  }
});

// visualViewport keyboard handling — biar chat-history ga ke-hide pas keyboard iOS naik
(function(){
  const chatHistory = document.querySelector(".chat-history");
  const chatInput = document.querySelector("#chat-input");
  if (!chatHistory) return;
  function handleViewportResize(){
    // delay 1 frame biar viewport udah settle
    requestAnimationFrame(() => scrollkebawah());
  }
  if (window.visualViewport){
    window.visualViewport.addEventListener('resize', handleViewportResize);
    window.visualViewport.addEventListener('scroll', handleViewportResize);
  }
  if (chatInput){
    chatInput.addEventListener('focus', () => {
      setTimeout(() => {
        chatInput.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
        scrollkebawah();
      }, 300);
    });
  }
  // fix dvh fallback untuk browser yang ga support dvh
  function setVh(){
    if (CSS.supports('height: 100dvh')) return;
    const vh = window.innerHeight * 0.01;
    document.documentElement.style.setProperty('--vh', vh + 'px');
  }
  setVh();
  window.addEventListener('resize', setVh);
})();

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

let lastFailedPesan = null;

function showRetryButton(pesan, aiBubble) {
  const retryWrapper = document.createElement("div");
  retryWrapper.className = "retry-wrapper";
  retryWrapper.style.cssText = "align-self:flex-start; margin:6px 0 8px 0;";
  const retryBtn = document.createElement("button");
  retryBtn.textContent = "Coba lagi";
  retryBtn.className = "retry-button";
  retryBtn.style.cssText = "padding:8px 16px; border-radius:999px; border:1px solid rgba(175,157,128,.4); background:rgba(255,255,255,.06); color:#FBFBFB; cursor:pointer; font-size:13px; font-family: Poppins, sans-serif;";
  retryBtn.addEventListener("click", () => {
    retryWrapper.remove();
    if (aiBubble && aiBubble.parentNode) {
      aiBubble.remove();
      updateClearButton();
    }
    kirimPesan(pesan);
  });
  retryWrapper.appendChild(retryBtn);
  messages.appendChild(retryWrapper);
  scrollkebawah();
}

async function kirimPesan(pesan){
  welcomeScreen.style.display = "none";
  buatBubble("User", pesan);
  input.value = "";
  setSending(true);
  lastFailedPesan = pesan;
  const typing = tampilkanTyping();
  let aiBubble = null;
  let hasStreamed = false;
  let buffer = "";
  let charQueue = [];
  let flushTimer = null;
  let doneReceived = false;
  let streamFinished = false;
  let isTypingRemoved = false;

  function startFlush() {
    if (flushTimer) return;
    flushTimer = setInterval(() => {
      if (charQueue.length > 0 && !isTypingRemoved) {
        if (typing && typing.parentNode) typing.remove();
        isTypingRemoved = true;
      }
      if (charQueue.length > 0) {
        let burst = 1;
        if (charQueue.length > 50) burst = 3;
        else if (charQueue.length > 20) burst = 2;
        let chunk = "";
        for (let i = 0; i < burst && charQueue.length > 0; i++) {
          chunk += charQueue.shift();
        }
        aiBubble.textContent += chunk;
        hasStreamed = true;
        scrollkebawah();
      } else if (doneReceived && streamFinished) {
        clearInterval(flushTimer);
        flushTimer = null;
        setSending(false);
        scrollkebawahSmooth();
      }
    }, 20);
  }

  function stopFlushImmediate() {
    if (flushTimer) {
      clearInterval(flushTimer);
      flushTimer = null;
    }
  }

  try {
    const response = await fetch("/api/chat/stream", {
      method: "POST",
      body: new URLSearchParams({pesan: pesan})
    });
    if (!response.ok) {
      throw new Error("Stream HTTP " + response.status);
    }
    if (!response.body) {
      throw new Error("ReadableStream not supported");
    }
    aiBubble = document.createElement("div");
    aiBubble.className = "message AI";
    aiBubble.textContent = "";
    messages.appendChild(aiBubble);
    updateClearButton();
    startFlush();
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    buffer = "";
    while (true) {
      const { done, value } = await reader.read();
      if (done) {
        streamFinished = true;
        if (charQueue.length === 0) doneReceived = true;
        break;
      }
      buffer += decoder.decode(value, { stream: true });
      const parts = buffer.split("\n\n");
      buffer = parts.pop();
      for (const part of parts) {
        if (!part.startsWith("data:")) continue;
        const jsonStr = part.slice(5).trim();
        if (!jsonStr) continue;
        let data;
        try { data = JSON.parse(jsonStr); } catch (e) { continue; }
        if (data.token) {
          hasStreamed = true;
          for (const ch of data.token) charQueue.push(ch);
        }
        if (data.error) {
          if (!hasStreamed && charQueue.length === 0) {
            stopFlushImmediate();
            if (typing && typing.parentNode) typing.remove();
            isTypingRemoved = true;
            aiBubble.textContent = data.error;
            setSending(false);
          } else {
            doneReceived = true;
            streamFinished = true;
            const waitError = setInterval(() => {
              if (charQueue.length === 0) {
                clearInterval(waitError);
                const errDiv = document.createElement("div");
                errDiv.className = "stream-error";
                errDiv.style.cssText = "align-self:flex-start; font-size:13px; color:#ff9b9b; margin:4px 0 6px 4px;";
                errDiv.textContent = data.error;
                messages.appendChild(errDiv);
                showRetryButton(pesan, null);
                scrollkebawah();
              }
            }, 60);
          }
        }
        if (data.done) {
          doneReceived = true;
        }
      }
    }
    if (buffer.trim().startsWith("data:")) {
      try {
        const data = JSON.parse(buffer.trim().slice(5).trim());
        if (data.token) for (const ch of data.token) charQueue.push(ch);
        if (data.error && !hasStreamed && charQueue.length === 0) {
          stopFlushImmediate();
          if (typing && typing.parentNode) typing.remove();
          isTypingRemoved = true;
          aiBubble.textContent = data.error;
          setSending(false);
        }
        if (data.done) doneReceived = true;
      } catch (e) {}
    }
    if (doneReceived && charQueue.length === 0) {
      stopFlushImmediate();
      if (typing && typing.parentNode) typing.remove();
      isTypingRemoved = true;
      setSending(false);
      scrollkebawahSmooth();
    } else if (!doneReceived) {
      streamFinished = true;
      doneReceived = true;
    }
  } catch (error) {
    console.error("[STREAM ERROR]", error);
    if (aiBubble && (hasStreamed || charQueue.length > 0)) {
      doneReceived = true;
      streamFinished = true;
      const waitErr = setInterval(() => {
        if (charQueue.length === 0) {
          clearInterval(waitErr);
          if (flushTimer) {
            clearInterval(flushTimer);
            flushTimer = null;
          }
          if (typing && typing.parentNode) typing.remove();
          isTypingRemoved = true;
          const errDiv = document.createElement("div");
          errDiv.className = "stream-error";
          errDiv.style.cssText = "align-self:flex-start; font-size:13px; color:#ff9b9b; margin:4px 0 6px 4px;";
          errDiv.textContent = "Koneksi terputus di tengah. ";
          messages.appendChild(errDiv);
          showRetryButton(pesan, null);
          setSending(false);
          scrollkebawah();
        }
      }, 60);
    } else {
      stopFlushImmediate();
      if (aiBubble && aiBubble.parentNode) aiBubble.remove();
      if (typing && typing.parentNode) typing.remove();
      isTypingRemoved = true;
      try {
        const fallbackResp = await fetch("/api/chat", {
          method: "POST",
          body: new URLSearchParams({pesan: pesan})
        });
        const fallbackData = await fallbackResp.json();
        if (!fallbackResp.ok) {
          buatBubble("AI", fallbackData.error || "Terjadi kesalahan. Coba lagi.");
          showRetryButton(pesan, null);
        } else {
          buatBubble("AI", fallbackData.reply);
        }
      } catch (fallbackErr) {
        console.error(fallbackErr);
        if (typing && typing.parentNode) typing.remove();
        isTypingRemoved = true;
        const exists = document.querySelector(".stream-error");
        if (!exists) {
          const errDiv = document.createElement("div");
          errDiv.className = "stream-error";
          errDiv.style.cssText = "align-self:flex-start; font-size:13px; color:#ff9b9b; margin:4px 0 6px 4px;";
          errDiv.textContent = "Gagal terhubung. Periksa jaringan dan coba lagi.";
          messages.appendChild(errDiv);
          showRetryButton(pesan, null);
        }
      }
      setSending(false);
    }
    scrollkebawah();
  } finally {
    if (typing && typing.parentNode && !isTypingRemoved) typing.remove();
    if (doneReceived && charQueue.length === 0 && flushTimer === null) {
      setSending(false);
    } else if (!hasStreamed && charQueue.length === 0 && !doneReceived) {
      // will be handled by catch fallback
    }
  }
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
// safety net: trim history yang terlanjur punya leading newline/spasi akibat template lama + pre-wrap
document.querySelectorAll("#messages .message").forEach(el => {
  const t = el.textContent;
  const trimmed = t.trim();
  if (t !== trimmed) el.textContent = trimmed;
});
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

let pendingScroll = false;

function scrollkebawah(){
  const chatHistory = document.querySelector(".chat-history");
  if(!chatHistory) return;
  if(pendingScroll) return;
  pendingScroll = true;
  requestAnimationFrame(() => {
    pendingScroll = false;
    // instant during streaming — jauh lebih mulus, tidak jank seperti smooth tiap 60ms
    chatHistory.scrollTop = chatHistory.scrollHeight;
  });
}

function scrollkebawahSmooth(){
  const chatHistory = document.querySelector(".chat-history");
  if(!chatHistory) return;
  chatHistory.scrollTo({
    top: chatHistory.scrollHeight,
    behavior: "smooth"
  });
}
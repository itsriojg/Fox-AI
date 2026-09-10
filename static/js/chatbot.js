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
// kalau toChat, --s sudah di-set skala tutup di inline script chatbot.html biar overlay ketutup sebelum paint
// arrival lintas origin (?phase=toChat&ox=&oy=) dianggap toChat juga + koordinat
// disimpan ke sessionStorage biar tombol back punya titik asal
function bacaQueryToChat(){
  try {
    const q = new URLSearchParams(window.location.search);
    if (q.get('phase') !== 'toChat') return null;
    const qx = parseFloat(q.get('ox')), qy = parseFloat(q.get('oy'));
    // Fallback ke tengah viewport kalau koordinat tidak valid/cacat —
    // biar FAB selalu trigger cover->open walau URL kiriman kurang ox/oy.
    const cx = window.innerWidth / 2, cy = window.innerHeight / 2;
    const x = Number.isNaN(qx) ? cx : qx;
    const y = Number.isNaN(qy) ? cy : qy;
    return { x, y };
  } catch(e) { return null; }
}
const _queryArrival = bacaQueryToChat();
if (_queryArrival) {
  safeSet('mintifTransitionPhase', 'toChat');
  safeSet('mintifOriginX', _queryArrival.x);
  safeSet('mintifOriginY', _queryArrival.y);
  // query sudah dikonsumsi, bersihkan dari URL biar refresh tidak replay animasi
  try { history.replaceState(null, '', window.location.pathname); } catch(e) {}
}
const _isToChatArrival = safeGet('mintifTransitionPhase') === 'toChat';
if (!_isToChatArrival) {
  root.style.setProperty('--s', '0');
  overlay.style.removeProperty('--s');
  revealWelcome();
}

function maxRadiusFrom(x, y){
  const vw = window.innerWidth, vh = window.innerHeight;
  const dx = Math.max(x, vw - x);
  const dy = Math.max(y, vh - y);
  return Math.hypot(dx, dy);
}

// Overlay lingkaran 100px yang di-scale GPU (compositor, tanpa repaint):
// s = radius_tutup / 50. Jauh lebih mulus dari clip-path di HP kentang.
function scaleFor(x, y){
  return maxRadiusFrom(x, y) / 50;
}

// Samakan dengan sisi Vue: clamp titik origin ke dalam viewport tujuan.
// Kalau koordinat cacat/NaN (buka /chatbot langsung, session ke-clear) → tengah
// viewport, biar cover->open / expand tetap main, tidak loncat polos.
function clampOrigin(x, y){
  const vw = window.innerWidth || 1, vh = window.innerHeight || 1;
  if (Number.isNaN(x) || Number.isNaN(y)) return { x: vw / 2, y: vh / 2 };
  return { x: Math.min(Math.max(x, 0), vw), y: Math.min(Math.max(y, 0), vh) };
}

(function playEntranceIfNeeded(){
  if (!_isToChatArrival) return;

  const needsSplash = shouldShowSplash(true);

  // Pola mekarDari (sisi Vue): snap ketutup -> reflow sync -> buka transisi
  // -> double raf set --s:0. Double rAF biar browser sempat paint state awal
  // sebelum transisi (single rAF rawan ke-batch → animasi ke-skip/snap).
  const rc = clampOrigin(parseFloat(safeGet('mintifOriginX')), parseFloat(safeGet('mintifOriginY')));
  const x = rc.x, y = rc.y;

  overlay.classList.add('no-transition');
  root.style.setProperty('--ox', x + 'px');
  root.style.setProperty('--oy', y + 'px');
  root.style.setProperty('--s', scaleFor(x, y));
  overlay.getBoundingClientRect(); // reflow sync: snap ketutup pre-paint
  overlay.classList.remove('no-transition');

  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      root.style.setProperty('--s', '0');
      if (needsSplash) {
        // overlap 180ms biar circle udah kebuka 20% baru logo mulai, zoom 0.08→1 jadi keliatan
        const t = setTimeout(playMintifSplash, 180);
        splashTimers.push(t);
      }
    });
  });

  safeRemove('mintifTransitionPhase');

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
      if (e.propertyName !== 'transform') return;
      doReveal();
    }
    overlay.addEventListener('transitionend', onEnd);
  }
})();

function handleBackNavigation(dariTombolWeb) {
  // Tujuan pulang: home web HIMATIF (env HOME_URL, default "/" = home Flask standalone).
  const homeBase = (typeof window.MINTIF_HOME_URL === 'string' && window.MINTIF_HOME_URL)
    ? window.MINTIF_HOME_URL.replace(/\/+$/, '')
    : '';

  if (backButton.dataset.leaving) return;

  backButton.dataset.leaving = "true";

  let cx, cy;
  if (dariTombolWeb) {
    // Klik tombol back web: mekar dari titik tengah tombol yang dipencet
    // (mirror titikTombol() FAB di MintifFab.vue). Fallback berlapis kalau
    // rect gagal kebaca: origin session warisan arrival -> tengah viewport.
    let bx = NaN, by = NaN;
    try {
      const r = backButton.getBoundingClientRect();
      if (r) { bx = r.left + r.width / 2; by = r.top + r.height / 2; }
    } catch(e) {}
    if (Number.isNaN(bx) || Number.isNaN(by)) {
      bx = parseFloat(safeGet('mintifOriginX'));
      by = parseFloat(safeGet('mintifOriginY'));
    }
    // Clamp + fallback tengah viewport (jangan href polos tanpa query):
    // biar pulang selalu bawa ?phase=toHome&ox&oy valid dan reverse-nya main.
    const c = clampOrigin(bx, by);
    cx = c.x; cy = c.y;
  } else {
    // Back HP (popstate): pertahankan perilaku lama — origin dari session
    // warisan arrival, jangan diubah.
    const x = parseFloat(safeGet('mintifOriginX'));
    const y = parseFloat(safeGet('mintifOriginY'));

    // Clamp + fallback tengah viewport (jangan href polos tanpa query):
    // biar pulang selalu bawa ?phase=toHome&ox&oy valid dan reverse-nya main.
    const c = clampOrigin(x, y);
    cx = c.x; cy = c.y;
  }
  safeSet('mintifOriginX', cx);
  safeSet('mintifOriginY', cy);

  overlay.classList.add('no-transition');
  root.style.setProperty('--ox', cx + 'px');
  root.style.setProperty('--oy', cy + 'px');
  root.style.setProperty('--s', '0'); // snap explicit dari 0 (sama kayak mekarDari Vue)

  overlay.getBoundingClientRect();

  overlay.classList.remove('no-transition');

  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      root.style.setProperty('--s', scaleFor(cx, cy));
    });
  });

  safeSet('mintifTransitionPhase', 'toHome');

  function onEnd(e) {
    if (e.propertyName !== 'transform') return
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
    // pulang lintas origin: tempel titik origin di query biar home HIMATIF
    // bisa snap ketutup pre-paint lalu susut (reverse circle reveal)
    const sep = homeBase.indexOf('?') === -1 ? '?' : '&';
    window.location.href = homeBase + "/" + sep + "phase=toHome&ox=" + Math.round(cx) + "&oy=" + Math.round(cy);
  };

  // Navigate pas 70% animasi (455ms dari 650ms)
  // Supaya loading bar ketutupan overlay
  fallbackTimer = setTimeout(goHome, 455);
}

backButton.addEventListener("click", () => handleBackNavigation(true));

// Back HP ≡ back web: pushState pas load, popstate -> handleBackNavigation().
// Biar tombol back fisik HP/konsumen ngereduksi ke home (circle reverse) juga.
// Guard lama (cuma fire kalau phase toHome/backNav) salah: saat normal phase=null
// sehingga trap tidak pernah fire dan back HP jadi native back ke halaman Vue
// frozen mid-cover (layar hitam). Sekarang intercept tiap back (kecuali lagi
// leaving) + pushState ulang biar back berikutnya tetap tertahan.
// Entry dikasih hash #mintif-chat (bukan pathname polos) biar system back HP
// reliably mendarat di entry same-document; tidak ada kode yang baca hash
// (aman), dan arrival replaceState membersihkannya.
(function(){
  var trapUrl = null;
  try { trapUrl = window.location.pathname + '#mintif-chat'; } catch(e) {}
  try { history.pushState(null, '', trapUrl || window.location.pathname); } catch(e) {}
  window.addEventListener('popstate', () => {
    if (backButton.dataset.leaving) return;
    try { history.pushState(null, '', trapUrl || window.location.pathname); } catch(e) {}
    handleBackNavigation();
  });
})();

// Handle mobile back button via pagehide (lebih aman dari beforeunload untuk BFCache)
window.addEventListener('pagehide', () => {
  if (!safeGet('mintifTransitionPhase')) {
    safeSet('mintifBackNavigation', 'true');
  }
});

// Fallback: pageshow untuk BFCache scenario
window.addEventListener('pageshow', (event) => {
  if (event.persisted && safeGet('mintifTransitionPhase') === 'toChat') {
    const needsSplash = shouldShowSplash(true);
    overlay.style.removeProperty('--s');
    requestAnimationFrame(() => {
      overlay.classList.remove('no-transition');
      overlay.getBoundingClientRect();
      requestAnimationFrame(() => {
        root.style.setProperty('--s', '0');
        if (needsSplash) {
          const t = setTimeout(playMintifSplash, 180);
          splashTimers.push(t);
        }
      });
    });
    safeRemove('mintifTransitionPhase');
    if (!needsSplash) {
      let revealed = false;
      const doReveal = () => {
        if (revealed) return;
        revealed = true;
        overlay.removeEventListener('transitionend', onEnd);
        revealWelcome();
      };
      function onEnd(e){
        if (e.propertyName !== 'transform') return;
        doReveal();
      }
      overlay.addEventListener('transitionend', onEnd);
      const fb = setTimeout(doReveal, 700);
      splashTimers.push(fb);
    }
  } else if (event.persisted && !safeGet('mintifTransitionPhase')) {
    // BFCache restore normal — jangan paksa redirect ke '/', cukup reveal welcome
    // biar ga blackscreen (fix: sebelumnya window.location.href='/' bikin loop)
    root.style.setProperty('--s', '0');
    overlay.style.removeProperty('--s');
    overlay.classList.remove('no-transition');
    revealWelcome();
  } else if (event.persisted && safeGet('mintifTransitionPhase') === 'toHome') {
    // Restore BFCache pas lagi ke-cover ke home — stale cover, reset biar ga hitam.
    safeRemove('mintifTransitionPhase');
    safeRemove('mintifBackNavigation');
    root.style.setProperty('--s', '0');
    overlay.style.removeProperty('--s');
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

// Mini markdown renderer (vanilla, tanpa dep): bold, italic, heading,
// list, code inline, link http(s). Tabel/HR/code-block TIDAK dirender.
// Selalu escape HTML dulu → tahan XSS. Cuma dipakai untuk bubble AI.
function escapeHtml(s){
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}
function renderInline(s){
  s = s.replace(/`([^`\n]+)`/g, "<code>$1</code>");
  s = s.replace(/\[([^\]\n]+)\]\((https?:\/\/[^)\s]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');
  s = s.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  s = s.replace(/(^|[^*\w])\*([^*\n]+)\*/g, "$1<em>$2</em>");
  return s;
}
function renderMarkdown(raw){
  const lines = escapeHtml(raw).split("\n");
  let html = "", inUL = false, inOL = false, para = [];
  function closeLists(){
    if (inUL){ html += "</ul>"; inUL = false; }
    if (inOL){ html += "</ol>"; inOL = false; }
  }
  function flushPara(){
    if (para.length){ html += "<p>" + para.join("<br>") + "</p>"; para = []; }
  }
  for (const line of lines){
    let m;
    if ((m = line.match(/^\s{0,3}#{1,3}\s+(.*)$/))){
      closeLists(); flushPara();
      html += "<h3>" + renderInline(m[1].trim()) + "</h3>";
    } else if ((m = line.match(/^\s*[-*]\s+(.*)$/))){
      flushPara();
      if (!inUL){ closeLists(); html += "<ul>"; inUL = true; }
      html += "<li>" + renderInline(m[1]) + "</li>";
    } else if ((m = line.match(/^\s*\d+\.\s+(.*)$/))){
      flushPara();
      if (!inOL){ closeLists(); html += "<ol>"; inOL = true; }
      html += "<li>" + renderInline(m[1]) + "</li>";
    } else if (line.trim() === ""){
      closeLists(); flushPara();
    } else {
      closeLists(); para.push(renderInline(line));
    }
  }
  closeLists(); flushPara();
  return html;
}
function renderAIBubble(el, raw){
  el.innerHTML = renderMarkdown(raw);
}

async function kirimPesan(pesan){
  welcomeScreen.style.display = "none";
  buatBubble("User", pesan);
  input.value = "";
  setSending(true);
  lastFailedPesan = pesan;
  const typing = tampilkanTyping();
  let aiBubble = null;
  let aiRaw = "";
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
        aiRaw += chunk;
        renderAIBubble(aiBubble, aiRaw);
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

const CLEAR_SVG = clearButton.innerHTML;
let confirmTimer = null;
function batalConfirm(){
  clearButton.classList.remove("confirm");
  clearButton.innerHTML = CLEAR_SVG;
  clearButton.setAttribute("aria-label", "Hapus riwayat chat");
  if (confirmTimer){ clearTimeout(confirmTimer); confirmTimer = null; }
}

clearForm.addEventListener("submit", (event) => {
  event.preventDefault();
  if (clearButton.disabled) return;
  // step 1: tap sekali -> mode konfirmasi (auto-batal 3 detik)
  if (!clearButton.classList.contains("confirm")) {
    clearButton.classList.add("confirm");
    clearButton.textContent = "Yakin?";
    clearButton.setAttribute("aria-label", "Ketuk lagi untuk hapus riwayat chat di layar ini");
    confirmTimer = setTimeout(batalConfirm, 3000);
    return;
  }
  // step 2: tap lagi -> eksekusi
  if (confirmTimer){ clearTimeout(confirmTimer); confirmTimer = null; }
  fetch("/clear", { method: "POST" })
    .then(() => {
      messages.innerHTML = "";
      welcomeScreen.style.display = "";
      input.value = "";
      setSending(false);
      batalConfirm();
      updateClearButton();
    })
    .catch((error) => { console.error(error); batalConfirm(); });
});

function buatBubble(sender, text){
  const bubble = document.createElement("div");
  bubble.className = "message " + sender;
  // cuma bubble AI yang di-render markdown; bubble user tetap teks polos
  if (sender === "AI") renderAIBubble(bubble, text);
  else bubble.textContent = text;
  messages.appendChild(bubble);

  updateClearButton();
  scrollkebawah();
  }

if(messages.children.length > 0){
  welcomeScreen.style.display = "none";
}
// safety net: trim history yang terlanjur punya leading newline/spasi akibat template lama + pre-wrap
// + render markdown untuk bubble AI dari server (Jinja autoescape kirim raw text)
document.querySelectorAll("#messages .message").forEach(el => {
  const t = el.textContent;
  const trimmed = t.trim();
  if (el.classList.contains("AI")) renderAIBubble(el, trimmed);
  else if (t !== trimmed) el.textContent = trimmed;
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
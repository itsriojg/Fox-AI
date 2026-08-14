const overlay = document.querySelector("#circleOverlay");
const fab = document.querySelector("#foxFab");
const root = document.documentElement;

function maxRadiusFrom(x, y){
  const vw = window.innerWidth, vh = window.innerHeight;
  const dx = Math.max(x, vw - x);
  const dy = Math.max(y, vh - y);
  return Math.hypot(dx, dy);
}

function setOverlayOrigin(x, y){
  root.style.setProperty('--ox', x + 'px');
  root.style.setProperty('--oy', y + 'px');
}

(function playReturnIfNeeded(){
  const phase = sessionStorage.getItem('foxTransitionPhase');
  if (phase !== 'toHome') return;

  requestAnimationFrame(() => {
    overlay.classList.remove('no-transition');
    requestAnimationFrame(() => {
      root.style.setProperty('--r', '0px');
    });
  });

  sessionStorage.removeItem('foxTransitionPhase');
  sessionStorage.removeItem('foxOriginX');
  sessionStorage.removeItem('foxOriginY');
})();

fab.addEventListener('click', (event) => {
  event.preventDefault();

  const rect = fab.getBoundingClientRect();
  const x = rect.left + rect.width / 2;
  const y = rect.top + rect.height / 2;

  setOverlayOrigin(x, y);
  root.style.setProperty('--r', '0px');
  overlay.getBoundingClientRect(); // flush

  requestAnimationFrame(() => {
    root.style.setProperty('--r', maxRadiusFrom(x, y) + 'px');
  });

  sessionStorage.setItem('foxOriginX', x);
  sessionStorage.setItem('foxOriginY', y);
  sessionStorage.setItem('foxTransitionPhase', 'toChat');

  overlay.addEventListener('transitionend', function onEnd(e){
    if (e.propertyName !== 'clip-path') return;
    overlay.removeEventListener('transitionend', onEnd);
    window.location.href = "/chatbot";
  });
});
// Home vanilla — port 1:1 dari home-react/src/App.jsx (keys mintif*)
(function(){
  var overlay = document.getElementById('circleOverlay');
  var fab = document.getElementById('mintifFab');
  var root = document.documentElement;
  if (!overlay || !fab) return;

  function maxRadiusFrom(x, y){
    var vw = window.innerWidth;
    var vh = window.innerHeight;
    var dx = Math.max(x, vw - x);
    var dy = Math.max(y, vh - y);
    return Math.hypot(dx, dy);
  }

  // Overlay lingkaran 100px yang di-scale GPU (sama kayak chatbot.js):
  // s = radius_tutup / 50.
  function scaleFor(x, y){
    return maxRadiusFrom(x, y) / 50;
  }

  function setOverlayOrigin(x, y){
    root.style.setProperty('--ox', x + 'px');
    root.style.setProperty('--oy', y + 'px');
  }

  function safeGet(k){ try{ return sessionStorage.getItem(k); }catch(e){ return null; } }
  function safeSet(k,v){ try{ sessionStorage.setItem(k,v); }catch(e){} }
  function safeRemove(k){ try{ sessionStorage.removeItem(k); }catch(e){} }

  // Animasi saat kembali ke Home
  function playReturnAnimation(){
    var phase = safeGet('mintifTransitionPhase');
    var backNav = safeGet('mintifBackNavigation');

    if (phase === 'toHome' || backNav === 'true'){
      var x = parseFloat(safeGet('mintifOriginX'));
      var y = parseFloat(safeGet('mintifOriginY'));
      root.style.setProperty('--ox', x + 'px');
      root.style.setProperty('--oy', y + 'px');

      // overlay statik + inline script udah cover layar di s = tutup
      // tinggal animate shrink buka home
      requestAnimationFrame(function(){
        overlay.classList.remove('no-transition');

        requestAnimationFrame(function(){
          root.style.setProperty('--s', '0');
        });
      });

      safeRemove('mintifTransitionPhase');
      safeRemove('mintifBackNavigation');
      safeRemove('mintifOriginX');
      safeRemove('mintifOriginY');

      delete fab.dataset.leaving;
    }
  }

  playReturnAnimation();

  // Handle mobile back button (pageshow event untuk BFCache)
  window.addEventListener('pageshow', function(event){
    if (event.persisted){
      playReturnAnimation();
    }
  });

  fab.addEventListener('click', function handleClick(event){
    event.preventDefault();

    // guard biar nggak dobel eksekusi kalau di-spam
    if (fab.dataset.leaving) return;

    var rect = fab.getBoundingClientRect();

    var x = rect.left + rect.width / 2;
    var y = rect.top + rect.height / 2;

    fab.dataset.leaving = 'true';

    // snap origin + skala 0 secara instan (tanpa transisi) dulu
    overlay.classList.add('no-transition');

    setOverlayOrigin(x, y);

    root.style.setProperty('--s', '0');

    overlay.getBoundingClientRect();

    overlay.classList.remove('no-transition');

    // Double rAF (sama kayak playReturnAnimation di atas): biar browser sempat
    // paint state snap sebelum transisi, single rAF rawan ke-batch → ke-skip.
    requestAnimationFrame(function(){
      requestAnimationFrame(function(){
        root.style.setProperty('--s', scaleFor(x, y));
      });
    });

    safeSet('mintifOriginX', x);
    safeSet('mintifOriginY', y);
    safeSet('mintifTransitionPhase', 'toChat');

    var done = false;
    var cleanupDone = false;
    var fallbackTimer = null;

    var cleanup = function(){
      if (cleanupDone) return;
      cleanupDone = true;
      overlay.removeEventListener('transitionend', handleTransitionEnd);
      if (fallbackTimer) clearTimeout(fallbackTimer);
    };

    var goToChat = function(){
      if (done) return;
      done = true;
      cleanup();

      // Navigate segera tanpa tunggu transisi selesai
      window.location.href = '/chatbot';
    };

    function handleTransitionEnd(e){
      if (e.propertyName !== 'transform') return;
      goToChat();
    }

    overlay.addEventListener('transitionend', handleTransitionEnd);

    // Navigate pas 70% animasi (455ms dari 650ms)
    fallbackTimer = setTimeout(goToChat, 455);
  });

  window.addEventListener('popstate', function(){
    var phase = safeGet('mintifTransitionPhase');
    var backNav = safeGet('mintifBackNavigation');
    if (phase === 'toHome' || backNav === 'true'){
      playReturnAnimation();
    }
    try{ history.pushState(null, '', location.href); }catch(e){}
  });
})();

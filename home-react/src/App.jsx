import { useEffect, useRef } from 'react'
import './App.css'

import Hero from './components/Hero'
import FoxButton from './components/FoxButton'

function App() {
  const fabRef = useRef(null)

  useEffect(() => {
    // overlay sekarang elemen statik di index.html biar bisa cover
    // layar sejak frame pertama (sebelum React mount)
    const overlay = document.getElementById('circleOverlay')
    const fab = fabRef.current
    const root = document.documentElement

    function maxRadiusFrom(x, y) {
      const vw = window.innerWidth
      const vh = window.innerHeight

      const dx = Math.max(x, vw - x)
      const dy = Math.max(y, vh - y)

      return Math.hypot(dx, dy)
    }

    function setOverlayOrigin(x, y) {
      root.style.setProperty('--ox', `${x}px`)
      root.style.setProperty('--oy', `${y}px`)
    }

    // Animasi saat kembali ke Home
    function playReturnAnimation() {
      const phase = sessionStorage.getItem('foxTransitionPhase')
      const backNav = sessionStorage.getItem('foxBackNavigation')
      
      if (phase === 'toHome' || backNav === 'true') {
        const x = parseFloat(sessionStorage.getItem('foxOriginX'))
        const y = parseFloat(sessionStorage.getItem('foxOriginY'))
        root.style.setProperty('--ox', `${x}px`)
        root.style.setProperty('--oy', `${y}px`)

        // overlay statik + inline script udah cover layar di r = max
        // tinggal animate shrink buka home
        requestAnimationFrame(() => {
          overlay.classList.remove('no-transition')

          requestAnimationFrame(() => {
            root.style.setProperty('--r', '0px')
          })
        })

        sessionStorage.removeItem('foxTransitionPhase')
        sessionStorage.removeItem('foxBackNavigation')
        sessionStorage.removeItem('foxOriginX')
        sessionStorage.removeItem('foxOriginY')
        
        delete fab.dataset.leaving
      }
    }

    playReturnAnimation()

    // Handle mobile back button (pageshow event untuk BFCache)
    window.addEventListener('pageshow', (event) => {
      if (event.persisted) {
        playReturnAnimation()
      }
    })

    function handleClick(event) {
      event.preventDefault()

      // guard biar nggak dobel eksekusi kalau di-spam
      if (fab.dataset.leaving) return

      const rect = fab.getBoundingClientRect()

      const x = rect.left + rect.width / 2
      const y = rect.top + rect.height / 2

      fab.dataset.leaving = 'true'

      // snap origin + radius 0 secara instan (tanpa transisi) dulu,
      // kalau nggak transisi lama ke-interrupt dan origin-nya
      // keburu interpolasi dari tengah layar di klik pertama
      overlay.classList.add('no-transition')

      setOverlayOrigin(x, y)

      root.style.setProperty('--r', '0px')

      overlay.getBoundingClientRect()

      overlay.classList.remove('no-transition')

      requestAnimationFrame(() => {
        root.style.setProperty(
          '--r',
          `${maxRadiusFrom(x, y)}px`
        )
      })

      sessionStorage.setItem('foxOriginX', x)
      sessionStorage.setItem('foxOriginY', y)
      sessionStorage.setItem('foxTransitionPhase', 'toChat')

      let done = false
      let cleanupDone = false
      let fallbackTimer = null

      const cleanup = () => {
        if (cleanupDone) return
        cleanupDone = true
        overlay.removeEventListener(
          'transitionend',
          handleTransitionEnd
        )
        if (fallbackTimer) clearTimeout(fallbackTimer)
      }

      const goToChat = () => {
        if (done) return
        done = true
        cleanup()
        
        // Navigate segera tanpa tunggu transisi selesai
        // Jadi loading bar ketutupan overlay
        window.location.href = '/chatbot'
      }

      function handleTransitionEnd(e) {
        if (e.propertyName !== 'clip-path') return
        goToChat()
      }

      overlay.addEventListener('transitionend', handleTransitionEnd)

      // Navigate pas 70% animasi (sekitar 630ms dari 900ms)
      // Supaya loading bar ketutupan overlay
      fallbackTimer = setTimeout(goToChat, 630)
    }

    fab.addEventListener('click', handleClick)

    const handlePopState = () => {
      const phase = sessionStorage.getItem('foxTransitionPhase')
      const backNav = sessionStorage.getItem('foxBackNavigation')
      if (phase === 'toHome' || backNav === 'true') {
        playReturnAnimation()
      }
      history.pushState(null, '', location.href)
    }

    window.addEventListener('popstate', handlePopState)

    return () => {
      fab.removeEventListener('click', handleClick)
      window.removeEventListener('popstate', handlePopState)
    }
  }, [])

  return (
    <>
      <Hero />

      <FoxButton ref={fabRef} />
    </>
  )
}

export default App
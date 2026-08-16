import { useEffect, useRef } from 'react'
import './App.css'

import Hero from './components/Hero'
import FoxButton from './components/FoxButton'

function App() {
  const overlayRef = useRef(null)
  const fabRef = useRef(null)

  useEffect(() => {
    const overlay = overlayRef.current
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
    const phase = sessionStorage.getItem('foxTransitionPhase')

    if (phase === 'toHome') {
      const x = parseFloat(sessionStorage.getItem('foxOriginX'))
      const y = parseFloat(sessionStorage.getItem('foxOriginY'))

      if (!isNaN(x) && !isNaN(y)) {
        const vw = window.innerWidth
        const vh = window.innerHeight

        const r = Math.hypot(
          Math.max(x, vw - x),
          Math.max(y, vh - y)
        )

        root.style.setProperty('--ox', `${x}px`)
        root.style.setProperty('--oy', `${y}px`)
        root.style.setProperty('--r', `${r}px`)

        overlay.classList.add('no-transition')

        requestAnimationFrame(() => {
          overlay.classList.remove('no-transition')

          requestAnimationFrame(() => {
            root.style.setProperty('--r', '0px')
          })
        })
      }

      sessionStorage.removeItem('foxTransitionPhase')
      sessionStorage.removeItem('foxOriginX')
      sessionStorage.removeItem('foxOriginY')
    }

    function handleClick(event) {
      event.preventDefault()

      const rect = fab.getBoundingClientRect()

      const x = rect.left + rect.width / 2
      const y = rect.top + rect.height / 2

      setOverlayOrigin(x, y)

      root.style.setProperty('--r', '0px')

      overlay.getBoundingClientRect()

      requestAnimationFrame(() => {
        root.style.setProperty(
          '--r',
          `${maxRadiusFrom(x, y)}px`
        )
      })

      sessionStorage.setItem('foxOriginX', x)
      sessionStorage.setItem('foxOriginY', y)
      sessionStorage.setItem('foxTransitionPhase', 'toChat')

      function handleTransitionEnd(e) {
        if (e.propertyName !== 'clip-path') return

        overlay.removeEventListener(
          'transitionend',
          handleTransitionEnd
        )

        window.location.href = '/chatbot'
      }

      overlay.addEventListener(
        'transitionend',
        handleTransitionEnd
      )
    }

    fab.addEventListener('click', handleClick)

    return () => {
      fab.removeEventListener('click', handleClick)
    }
  }, [])

  return (
    <>
      <div
        ref={overlayRef}
        className="circle-overlay"
      />

      <Hero />

      <FoxButton ref={fabRef} />
    </>
  )
}

export default App
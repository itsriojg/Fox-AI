import { forwardRef } from 'react'

const FoxButton = forwardRef(function FoxButton(_, ref) {
  return (
    <button
      ref={ref}
      className="fox-floating"
      type="button"
      aria-label="Buka Fox AI Chatbot"
    >
      <img
        src="/react-assets/assets/floating-button-fox-ai.png"
        alt="Fox AI"
      />

      <span className="fox-tooltip">
        Tanya Fox AI
      </span>
    </button>
  )
})

export default FoxButton
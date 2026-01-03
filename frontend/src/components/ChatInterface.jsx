import { useState } from 'react'

const mockMessages = [
  { sender: 'User', text: 'Hi' },
  { sender: 'Agent', text: 'Hello! I am your Pharmacy Agent.' },
  { sender: 'User', text: 'Check stock for Aspirin' },
]

function ChatInterface() {
  const [draft, setDraft] = useState('')

  const handleSubmit = (event) => {
    event.preventDefault()
    setDraft('')
  }

  return (
    <div className="chat-container">
      <div className="chat-messages">
        {mockMessages.map((msg, idx) => (
          <div key={`${msg.sender}-${idx}`} className={`message ${msg.sender.toLowerCase()}`}>
            <span className="sender">{msg.sender}:</span>
            <span className="text">{msg.text}</span>
          </div>
        ))}
      </div>
      <form className="chat-input" onSubmit={handleSubmit}>
        <input
          type="text"
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          placeholder="Type a message"
          aria-label="Chat message"
        />
        <button type="submit">Send</button>
      </form>
    </div>
  )
}

export default ChatInterface

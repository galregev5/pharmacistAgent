import { useEffect, useRef, useState } from 'react'
import { Stethoscope } from 'lucide-react'

import { Avatar, AvatarFallback } from './ui/avatar'
import { Button } from './ui/button'
import { Card } from './ui/card'
import { Input } from './ui/input'
import { ScrollArea } from './ui/scroll-area'
import { sendMessage } from '../services/api'

const initialMessages = [
  { sender: 'agent', text: 'Hello! I am your Pharmacy Agent. How can I assist you today?' },
]

function ChatInterface() {
  const [draft, setDraft] = useState('')
  const [messages, setMessages] = useState(initialMessages)
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef(null)

  const handleSubmit = async (event) => {
    event.preventDefault()
    const text = draft.trim()
    if (!text) return

    const userMessage = { sender: 'user', text }
    const history = [...messages, userMessage]

    setMessages((prev) => [...prev, userMessage, { sender: 'agent', text: '' }])
    setDraft('')
    setIsLoading(true)

    try {
      const finalText = await sendMessage(text, history, (token) => {
        setMessages((prev) => {
          const next = [...prev]
          const lastIndex = next.length - 1
          if (next[lastIndex] && next[lastIndex].sender === 'agent') {
            next[lastIndex] = { ...next[lastIndex], text: (next[lastIndex].text || '') + token }
          }
          return next
        })
      })

      if (!finalText) {
        setMessages((prev) => {
          const next = [...prev]
          const lastIndex = next.length - 1
          if (next[lastIndex] && next[lastIndex].sender === 'agent') {
            next[lastIndex] = { ...next[lastIndex], text: 'Okay.' }
          }
          return next
        })
      }
    } catch (error) {
      setMessages((prev) => {
        const next = [...prev]
        const lastIndex = next.length - 1
        const fallback = 'Sorry, I could not reach the server. Please try again.'
        if (next[lastIndex] && next[lastIndex].sender === 'agent') {
          next[lastIndex] = { ...next[lastIndex], text: fallback }
        } else {
          next.push({ sender: 'agent', text: fallback })
        }
        return next
      })
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  return (
    <div className="flex h-full flex-1 flex-col bg-white">
      <div className="flex items-center gap-2 border-b bg-white px-6 py-4">
        <span className="h-2.5 w-2.5 rounded-full bg-emerald-500" aria-hidden />
        <p className="text-sm font-semibold text-slate-800">Agent Status: Online</p>
      </div>

      <ScrollArea className="flex-1 px-6 py-6">
        <div className="flex flex-col gap-4">
          {messages.map((msg, idx) => {
            const isAgent = msg.sender === 'agent'
            return (
              <div key={`${msg.sender}-${idx}`} className={`flex ${isAgent ? 'justify-start' : 'justify-end'}`}>
                <div className={`flex max-w-[70%] items-start gap-3 ${isAgent ? '' : 'flex-row-reverse'}`}>
                  {isAgent && (
                    <Avatar className="h-9 w-9 bg-slate-200 text-slate-700">
                      <AvatarFallback>
                        <Stethoscope className="h-4 w-4" />
                      </AvatarFallback>
                    </Avatar>
                  )}
                  <div
                    className={`rounded-2xl px-4 py-3 text-sm shadow-sm ${
                      isAgent ? 'bg-slate-100 text-slate-800' : 'bg-blue-600 text-white'
                    }`}
                  >
                    {msg.text}
                  </div>
                </div>
              </div>
            )
          })}

          {isLoading && (
            <div className="flex justify-start">
              <div className="flex max-w-[70%] items-start gap-3">
                <Avatar className="h-9 w-9 bg-slate-200 text-slate-700">
                  <AvatarFallback>
                    <Stethoscope className="h-4 w-4" />
                  </AvatarFallback>
                </Avatar>
                <div className="rounded-2xl bg-slate-100 px-4 py-3 text-sm text-slate-800 shadow-sm">
                  Thinking...
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </ScrollArea>

      <div className="pointer-events-none relative pb-6">
        <div className="pointer-events-auto mx-auto w-full max-w-3xl px-4">
          <Card className="shadow-lg">
            <form className="flex items-center gap-3 p-4" onSubmit={handleSubmit}>
              <Input
                value={draft}
                onChange={(e) => setDraft(e.target.value)}
                placeholder="Ask about medications..."
                aria-label="Chat message"
                disabled={isLoading}
              />
              <Button type="submit" disabled={isLoading}>
                {isLoading ? 'Sending...' : 'Send'}
              </Button>
            </form>
          </Card>
        </div>
      </div>
    </div>
  )
}

export default ChatInterface

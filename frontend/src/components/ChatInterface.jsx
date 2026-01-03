import { useState } from 'react'
import { Stethoscope } from 'lucide-react'

import { Avatar, AvatarFallback } from './ui/avatar'
import { Button } from './ui/button'
import { Card } from './ui/card'
import { Input } from './ui/input'
import { ScrollArea } from './ui/scroll-area'

const mockMessages = [
  { sender: 'agent', text: 'Hello! I am your Pharmacy Agent. How can I assist you today?' },
  { sender: 'user', text: 'Can you check stock for Aspirin 100mg?' },
  { sender: 'agent', text: 'Aspirin 100mg is in stock. Do you want me to reserve 1 pack?' },
]

function ChatInterface() {
  const [draft, setDraft] = useState('')

  const handleSubmit = (event) => {
    event.preventDefault()
    setDraft('')
  }

  return (
    <div className="flex h-full flex-1 flex-col bg-white">
      <div className="flex items-center gap-2 border-b bg-white px-6 py-4">
        <span className="h-2.5 w-2.5 rounded-full bg-emerald-500" aria-hidden />
        <p className="text-sm font-semibold text-slate-800">Agent Status: Online</p>
      </div>

      <ScrollArea className="flex-1 px-6 py-6">
        <div className="flex flex-col gap-4">
          {mockMessages.map((msg, idx) => {
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
              />
              <Button type="submit">Send</Button>
            </form>
          </Card>
        </div>
      </div>
    </div>
  )
}

export default ChatInterface

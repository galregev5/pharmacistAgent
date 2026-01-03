export async function sendMessage(message, history = [], onChunk) {
  try {
    const response = await fetch('http://127.0.0.1:5000/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'text/event-stream',
      },
      body: JSON.stringify({ message, history }),
    })

    if (!response.ok) {
      const text = await response.text()
      throw new Error(`API error ${response.status}: ${text}`)
    }

    if (!response.body) {
      throw new Error('Streaming response body is not supported in this browser.')
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder('utf-8')
    let buffer = ''
    let finalText = ''

    const processBuffer = () => {
      const parts = buffer.split('\n\n')
      buffer = parts.pop() || ''

      for (const part of parts) {
        const line = part.trim()
        if (!line.startsWith('data:')) continue

        const payload = line.replace(/^data:\s*/, '')
        if (payload === '[DONE]') {
          return { done: true }
        }

        try {
          const parsed = JSON.parse(payload)
          if (parsed.error) {
            return { done: true, error: parsed.error }
          }
          if (parsed.token) {
            finalText += parsed.token
            if (onChunk) onChunk(parsed.token)
          }
        } catch (err) {
          console.error('Failed to parse SSE chunk', err)
        }
      }

      return { done: false }
    }

    // eslint-disable-next-line no-constant-condition
    while (true) {
      const { value, done } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      const status = processBuffer()
      if (status.done) {
        if (status.error) throw new Error(status.error)
        return finalText
      }
    }

    buffer += decoder.decode()
    const status = processBuffer()
    if (status.error) throw new Error(status.error)
    return finalText
  } catch (error) {
    console.error('sendMessage failed. Is the backend running?', error)
    throw error
  }
}

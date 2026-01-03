export async function sendMessage(message, history = []) {
  try {
    const response = await fetch('http://127.0.0.1:5000/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message, history }),
    })

    if (!response.ok) {
      const text = await response.text()
      throw new Error(`API error ${response.status}: ${text}`)
    }

    return await response.json()
  } catch (error) {
    console.error('sendMessage failed. Is the backend running?', error)
    throw error
  }
}

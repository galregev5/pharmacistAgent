import './App.css'
import ChatInterface from './components/ChatInterface'

function App() {
  return (
    <main className="app-shell">
      <header className="app-header">
        <h1>Pharmacy Agent</h1>
      </header>
      <div className="status-tile">System Status: Connected</div>
      <ChatInterface />
    </main>
  )
}

export default App

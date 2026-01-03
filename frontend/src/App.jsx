import './App.css'
import ChatInterface from './components/ChatInterface'
import Sidebar from './components/Sidebar'

function App() {
  return (
    <div className="h-screen w-full overflow-hidden bg-slate-50">
      <div className="flex h-full">
        <Sidebar />
        <div className="flex-1">
          <ChatInterface />
        </div>
      </div>
    </div>
  )
}

export default App

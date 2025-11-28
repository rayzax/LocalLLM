import { ChatProvider } from './context/ChatContext'
import ConversationList from './components/Sidebar/ConversationList'
import ChatInterface from './components/Chat/ChatInterface'

function App() {
  return (
    <ChatProvider>
      <div className="flex h-screen bg-dark-950 overflow-hidden">
        <ConversationList />
        <div className="flex-1">
          <ChatInterface />
        </div>
      </div>
    </ChatProvider>
  )
}

export default App

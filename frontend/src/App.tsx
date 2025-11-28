import { useState } from 'react'
import { ChatProvider } from './context/ChatContext'
import ConversationList from './components/Sidebar/ConversationList'
import ChatInterface from './components/Chat/ChatInterface'
import DocumentsPanel from './components/Documents/DocumentsPanel'
import { MessageSquare, Database } from 'lucide-react'

type Tab = 'chat' | 'documents'

function App() {
  const [activeTab, setActiveTab] = useState<Tab>('chat')

  return (
    <ChatProvider>
      <div className="flex h-screen bg-black overflow-hidden">
        {/* Sidebar Navigation */}
        <div className="w-16 glass border-r border-primary-700/20 flex flex-col items-center py-4 gap-4">
          <button
            onClick={() => setActiveTab('chat')}
            className={`w-12 h-12 rounded-lg flex items-center justify-center transition-all ${
              activeTab === 'chat'
                ? 'bg-primary-600 glow'
                : 'hover:bg-primary-600/20 text-gray-400'
            }`}
            title="Chat"
          >
            <MessageSquare size={24} />
          </button>
          <button
            onClick={() => setActiveTab('documents')}
            className={`w-12 h-12 rounded-lg flex items-center justify-center transition-all ${
              activeTab === 'documents'
                ? 'bg-primary-600 glow'
                : 'hover:bg-primary-600/20 text-gray-400'
            }`}
            title="Documents"
          >
            <Database size={24} />
          </button>
        </div>

        {/* Main Content */}
        <div className="flex flex-1 overflow-hidden">
          {activeTab === 'chat' ? (
            <>
              <ConversationList />
              <div className="flex-1">
                <ChatInterface />
              </div>
            </>
          ) : (
            <div className="flex-1">
              <DocumentsPanel />
            </div>
          )}
        </div>
      </div>
    </ChatProvider>
  )
}

export default App

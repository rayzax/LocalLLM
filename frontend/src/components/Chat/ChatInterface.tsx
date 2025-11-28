import { useState, useEffect } from 'react'
import { useChat } from '../../context/ChatContext'
import MessageList from './MessageList'
import MessageInput from './MessageInput'
import ModelSelector from './ModelSelector'
import { Sparkles } from 'lucide-react'

export default function ChatInterface() {
  const { currentConversation, models } = useChat()
  const [selectedModel, setSelectedModel] = useState('llama3.2:3b')
  const [temperature, setTemperature] = useState(0.7)
  const [topP, setTopP] = useState(0.9)
  const [maxTokens, setMaxTokens] = useState<number | null>(null)

  // Update selected model when models are loaded
  useEffect(() => {
    if (models.length > 0 && !selectedModel) {
      setSelectedModel(models[0].name)
    }
  }, [models, selectedModel])

  // Update selected model when conversation changes
  useEffect(() => {
    if (currentConversation) {
      setSelectedModel(currentConversation.model)
    }
  }, [currentConversation])

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ctrl+K or Cmd+K for new chat
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault()
        // This will be handled by the ConversationList component
        const newChatButton = document.querySelector('[data-new-chat]') as HTMLButtonElement
        newChatButton?.click()
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [])

  return (
    <div className="flex flex-col h-screen">
      {/* Header */}
      <div className="flex-shrink-0 glass border-b border-primary-700/20 p-4">
        <div className="max-w-5xl mx-auto">
          <div className="flex items-center justify-between gap-6">
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <Sparkles size={20} className="text-primary-400" />
                <h2 className="text-lg font-semibold text-gray-200 truncate">
                  {currentConversation ? currentConversation.title : 'New Conversation'}
                </h2>
              </div>
              <p className="text-sm text-gray-400">
                {currentConversation
                  ? `${currentConversation.message_count} messages`
                  : 'Start chatting with your local LLM'}
              </p>
            </div>
            <div className="flex-shrink-0 w-72">
              <ModelSelector
                selectedModel={selectedModel}
                onModelChange={setSelectedModel}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Messages - This is the scrollable area */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-5xl mx-auto h-full">
          <MessageList />
        </div>
      </div>

      {/* Input - Fixed at bottom */}
      <div className="flex-shrink-0 glass border-t border-primary-700/20">
        <div className="max-w-5xl mx-auto">
          <MessageInput
            selectedModel={selectedModel}
            temperature={temperature}
            topP={topP}
            maxTokens={maxTokens}
            onTemperatureChange={setTemperature}
            onTopPChange={setTopP}
            onMaxTokensChange={setMaxTokens}
          />
        </div>
      </div>
    </div>
  )
}

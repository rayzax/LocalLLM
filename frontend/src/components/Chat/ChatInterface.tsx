import { useState, useEffect } from 'react'
import { useChat } from '../../context/ChatContext'
import MessageList from './MessageList'
import MessageInput from './MessageInput'
import ModelSelector from './ModelSelector'

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
    <div className="flex flex-col h-screen bg-dark-950">
      {/* Header */}
      <div className="border-b border-dark-800 bg-dark-900 p-4">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center justify-between gap-4">
            <div className="flex-1">
              <h2 className="text-lg font-semibold text-gray-200">
                {currentConversation ? currentConversation.title : 'New Conversation'}
              </h2>
              <p className="text-sm text-gray-500">
                {currentConversation
                  ? `${currentConversation.message_count} messages`
                  : 'Start chatting with your local LLM'}
              </p>
            </div>
            <div className="w-64">
              <ModelSelector
                selectedModel={selectedModel}
                onModelChange={setSelectedModel}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-hidden">
        <div className="max-w-4xl mx-auto h-full">
          <MessageList />
        </div>
      </div>

      {/* Input */}
      <div className="border-t border-dark-800">
        <div className="max-w-4xl mx-auto">
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

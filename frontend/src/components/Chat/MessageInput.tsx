import { useState, useRef, useEffect } from 'react'
import { Send, Settings } from 'lucide-react'
import { useChat } from '../../context/ChatContext'

interface MessageInputProps {
  selectedModel: string
  temperature: number
  topP: number
  maxTokens: number | null
  onTemperatureChange: (value: number) => void
  onTopPChange: (value: number) => void
  onMaxTokensChange: (value: number | null) => void
}

export default function MessageInput({
  selectedModel,
  temperature,
  topP,
  maxTokens,
  onTemperatureChange,
  onTopPChange,
  onMaxTokensChange
}: MessageInputProps) {
  const { sendMessage, isStreaming, currentConversation } = useChat()
  const [message, setMessage] = useState('')
  const [showSettings, setShowSettings] = useState(false)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px'
    }
  }, [message])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!message.trim() || isStreaming) return

    const content = message
    setMessage('')

    await sendMessage(content, {
      model: selectedModel,
      temperature,
      top_p: topP,
      max_tokens: maxTokens || undefined
    })
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  return (
    <div className="border-t border-dark-800 bg-dark-900 p-4">
      {/* Settings Panel */}
      {showSettings && (
        <div className="mb-4 p-4 bg-dark-800 rounded-lg space-y-4">
          <h3 className="text-sm font-semibold text-gray-300 mb-3">Model Parameters</h3>

          {/* Temperature */}
          <div>
            <div className="flex justify-between items-center mb-2">
              <label className="text-xs text-gray-400">Temperature</label>
              <span className="text-xs text-gray-500">{temperature.toFixed(2)}</span>
            </div>
            <input
              type="range"
              min="0"
              max="2"
              step="0.1"
              value={temperature}
              onChange={(e) => onTemperatureChange(parseFloat(e.target.value))}
              className="w-full h-2 bg-dark-700 rounded-lg appearance-none cursor-pointer accent-primary-500"
            />
            <p className="text-xs text-gray-600 mt-1">
              Higher values make output more random, lower values more focused
            </p>
          </div>

          {/* Top P */}
          <div>
            <div className="flex justify-between items-center mb-2">
              <label className="text-xs text-gray-400">Top P</label>
              <span className="text-xs text-gray-500">{topP.toFixed(2)}</span>
            </div>
            <input
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={topP}
              onChange={(e) => onTopPChange(parseFloat(e.target.value))}
              className="w-full h-2 bg-dark-700 rounded-lg appearance-none cursor-pointer accent-primary-500"
            />
            <p className="text-xs text-gray-600 mt-1">
              Nucleus sampling threshold
            </p>
          </div>

          {/* Max Tokens */}
          <div>
            <div className="flex justify-between items-center mb-2">
              <label className="text-xs text-gray-400">Max Tokens</label>
              <span className="text-xs text-gray-500">
                {maxTokens || 'Unlimited'}
              </span>
            </div>
            <input
              type="number"
              value={maxTokens || ''}
              onChange={(e) => onMaxTokensChange(e.target.value ? parseInt(e.target.value) : null)}
              placeholder="Unlimited"
              className="input w-full"
            />
            <p className="text-xs text-gray-600 mt-1">
              Maximum number of tokens to generate (leave empty for unlimited)
            </p>
          </div>
        </div>
      )}

      {/* Input Area */}
      <form onSubmit={handleSubmit} className="flex gap-2">
        <textarea
          ref={textareaRef}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={
            currentConversation
              ? "Type your message... (Ctrl+Enter to send)"
              : "Start a new conversation..."
          }
          disabled={isStreaming}
          className="input flex-1 resize-none min-h-[60px] max-h-[200px]"
          rows={1}
        />

        <div className="flex flex-col gap-2">
          <button
            type="button"
            onClick={() => setShowSettings(!showSettings)}
            className={`btn-ghost p-3 ${showSettings ? 'bg-dark-700' : ''}`}
            title="Model settings"
          >
            <Settings size={20} />
          </button>

          <button
            type="submit"
            disabled={!message.trim() || isStreaming}
            className="btn-primary p-3"
            title="Send message (Ctrl+Enter)"
          >
            <Send size={20} />
          </button>
        </div>
      </form>

      {/* Help Text */}
      <div className="mt-2 text-xs text-gray-600 flex items-center justify-between">
        <span>Press Ctrl+Enter to send</span>
        {isStreaming && <span className="text-primary-400">Generating response...</span>}
      </div>
    </div>
  )
}

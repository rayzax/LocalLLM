import { useEffect } from 'react'
import { MessageSquare, Plus, Trash2, Sparkles } from 'lucide-react'
import { useChat } from '../../context/ChatContext'
import { formatDistanceToNow } from 'date-fns'

export default function ConversationList() {
  const {
    conversations,
    currentConversation,
    selectConversation,
    deleteConversation,
    loadConversations
  } = useChat()

  useEffect(() => {
    loadConversations()
  }, [loadConversations])

  const handleNewChat = () => {
    selectConversation(null)
  }

  const handleDelete = async (e: React.MouseEvent, id: number) => {
    e.stopPropagation()
    if (confirm('Delete this conversation?')) {
      try {
        await deleteConversation(id)
      } catch (error) {
        console.error('Failed to delete conversation:', error)
      }
    }
  }

  return (
    <div className="sidebar w-64 flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-primary-700/20">
        <div className="flex items-center gap-2 mb-4">
          <Sparkles size={24} className="text-primary-400" />
          <h1 className="text-xl font-bold text-gradient">LLMLocal</h1>
        </div>
        <button
          onClick={handleNewChat}
          data-new-chat
          className="btn-primary w-full flex items-center justify-center gap-2"
        >
          <Plus size={18} />
          New Chat
        </button>
      </div>

      {/* Conversation List */}
      <div className="flex-1 overflow-y-auto p-2">
        {conversations.length === 0 ? (
          <div className="text-center text-gray-500 mt-8 px-4">
            <MessageSquare size={48} className="mx-auto mb-2 opacity-30 text-primary-400" />
            <p className="text-sm text-gray-400">No conversations yet</p>
            <p className="text-xs mt-1 text-gray-500">Start a new chat to begin</p>
          </div>
        ) : (
          <div className="space-y-1">
            {conversations.map((conv) => (
              <div
                key={conv.id}
                onClick={() => selectConversation(conv)}
                className={`
                  group p-3 rounded-lg cursor-pointer transition-all
                  ${currentConversation?.id === conv.id
                    ? 'glass border-primary-600/40 glow'
                    : 'hover:glass border-transparent'
                  }
                `}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex-1 min-w-0">
                    <h3 className="text-sm font-medium text-gray-200 truncate">
                      {conv.title}
                    </h3>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="text-xs text-primary-400">
                        {conv.message_count} msgs
                      </span>
                      <span className="text-xs text-gray-600">•</span>
                      <span className="text-xs text-gray-500">
                        {formatDistanceToNow(new Date(conv.updated_at), { addSuffix: true })}
                      </span>
                    </div>
                  </div>
                  <button
                    onClick={(e) => handleDelete(e, conv.id)}
                    className="opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:bg-red-900/20 rounded"
                    title="Delete conversation"
                  >
                    <Trash2 size={14} className="text-red-400" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-primary-700/20 text-xs text-gray-500">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 bg-primary-500 rounded-full animate-pulse-slow glow"></div>
          <span className="text-gray-400">Connected to Ollama</span>
        </div>
      </div>
    </div>
  )
}

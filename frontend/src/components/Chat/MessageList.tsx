import { useEffect, useRef } from 'react'
import { User, Bot, Loader2 } from 'lucide-react'
import { useChat } from '../../context/ChatContext'
import ReactMarkdown from 'react-markdown'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism'

export default function MessageList() {
  const { messages, isStreaming, streamingMessage } = useChat()
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, streamingMessage])

  return (
    <div className="h-full p-6 space-y-6">
      {messages.length === 0 && !isStreaming && (
        <div className="flex items-center justify-center h-full">
          <div className="text-center text-gray-500">
            <div className="relative inline-block">
              <Bot size={64} className="mx-auto mb-4 opacity-30 text-primary-400" />
              <div className="absolute inset-0 blur-xl bg-primary-500/20 rounded-full"></div>
            </div>
            <h2 className="text-2xl font-semibold mb-2 text-gradient">
              Start a conversation
            </h2>
            <p className="text-sm text-gray-400">
              Type your message below to begin chatting with your AI
            </p>
          </div>
        </div>
      )}

      {messages.map((message) => (
        <div
          key={message.id}
          className={`flex gap-4 ${
            message.role === 'user' ? 'justify-end' : 'justify-start'
          }`}
        >
          {message.role === 'assistant' && (
            <div className="flex-shrink-0 w-10 h-10 rounded-lg bg-gradient-to-br from-primary-600 to-primary-800 flex items-center justify-center glow">
              <Bot size={20} className="text-white" />
            </div>
          )}

          <div
            className={`max-w-3xl ${
              message.role === 'user' ? 'message-user' : 'message-assistant'
            }`}
          >
            <div className="prose prose-invert max-w-none">
              <ReactMarkdown
                components={{
                  code(props) {
                    const {children, className, node, ref, ...rest} = props
                    const match = /language-(\w+)/.exec(className || '')

                    return match ? (
                      <SyntaxHighlighter
                        PreTag="div"
                        language={match[1]}
                        style={vscDarkPlus as any}
                      >
                        {String(children).replace(/\n$/, '')}
                      </SyntaxHighlighter>
                    ) : (
                      <code className={className}>
                        {children}
                      </code>
                    )
                  }
                }}
              >
                {message.content}
              </ReactMarkdown>
            </div>
          </div>

          {message.role === 'user' && (
            <div className="flex-shrink-0 w-10 h-10 rounded-lg bg-gradient-to-br from-secondary-500 to-secondary-700 flex items-center justify-center glow">
              <User size={20} className="text-white" />
            </div>
          )}
        </div>
      ))}

      {/* Streaming Message */}
      {isStreaming && streamingMessage && (
        <div className="flex gap-4 justify-start">
          <div className="flex-shrink-0 w-10 h-10 rounded-lg bg-gradient-to-br from-primary-600 to-primary-800 flex items-center justify-center glow animate-pulse">
            <Bot size={20} className="text-white" />
          </div>

          <div className="max-w-3xl message-assistant">
            <div className="prose prose-invert max-w-none">
              <ReactMarkdown
                components={{
                  code(props) {
                    const {children, className, node, ref, ...rest} = props
                    const match = /language-(\w+)/.exec(className || '')

                    return match ? (
                      <SyntaxHighlighter
                        PreTag="div"
                        language={match[1]}
                        style={vscDarkPlus as any}
                      >
                        {String(children).replace(/\n$/, '')}
                      </SyntaxHighlighter>
                    ) : (
                      <code className={className}>
                        {children}
                      </code>
                    )
                  }
                }}
              >
                {streamingMessage}
              </ReactMarkdown>
            </div>
            <div className="flex items-center gap-2 mt-2 text-xs text-primary-400">
              <Loader2 size={12} className="animate-spin" />
              <span>Generating...</span>
            </div>
          </div>
        </div>
      )}

      <div ref={messagesEndRef} />
    </div>
  )
}

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
    <div className="flex-1 overflow-y-auto p-6 space-y-6">
      {messages.length === 0 && !isStreaming && (
        <div className="flex items-center justify-center h-full">
          <div className="text-center text-gray-500">
            <Bot size={64} className="mx-auto mb-4 opacity-30" />
            <h2 className="text-2xl font-semibold mb-2 text-gray-400">
              Start a conversation
            </h2>
            <p className="text-sm">
              Type your message below to begin chatting with the AI
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
            <div className="flex-shrink-0 w-8 h-8 rounded-lg bg-primary-600 flex items-center justify-center">
              <Bot size={18} className="text-white" />
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
                    const { children, className, ref, ...rest } = props
                    const match = /language-(\w+)/.exec(className || '')

                    return match ? (
                      <SyntaxHighlighter
                        {...rest}
                        PreTag="div"
                        language={match[1]}
                        style={vscDarkPlus as any}
                      >
                        {String(children).replace(/\n$/, '')}
                      </SyntaxHighlighter>
                    ) : (
                      <code {...rest} className={className}>
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
            <div className="flex-shrink-0 w-8 h-8 rounded-lg bg-secondary-500 flex items-center justify-center">
              <User size={18} className="text-white" />
            </div>
          )}
        </div>
      ))}

      {/* Streaming Message */}
      {isStreaming && streamingMessage && (
        <div className="flex gap-4 justify-start">
          <div className="flex-shrink-0 w-8 h-8 rounded-lg bg-primary-600 flex items-center justify-center">
            <Bot size={18} className="text-white" />
          </div>

          <div className="max-w-3xl message-assistant">
            <div className="prose prose-invert max-w-none">
              <ReactMarkdown
                components={{
                  code(props) {
                    const { children, className, ref, ...rest } = props
                    const match = /language-(\w+)/.exec(className || '')

                    return match ? (
                      <SyntaxHighlighter
                        {...rest}
                        PreTag="div"
                        language={match[1]}
                        style={vscDarkPlus as any}
                      >
                        {String(children).replace(/\n$/, '')}
                      </SyntaxHighlighter>
                    ) : (
                      <code {...rest} className={className}>
                        {children}
                      </code>
                    )
                  }
                }}
              >
                {streamingMessage}
              </ReactMarkdown>
            </div>

            <div className="flex items-center gap-2 mt-2 text-xs text-gray-500">
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

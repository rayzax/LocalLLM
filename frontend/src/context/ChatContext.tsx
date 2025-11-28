import { createContext, useContext, useState, useCallback, ReactNode } from 'react'
import { api } from '../services/api'
import type { Conversation, Message, Model } from '../types'

interface ChatContextType {
  conversations: Conversation[]
  currentConversation: Conversation | null
  messages: Message[]
  models: Model[]
  isLoading: boolean
  isStreaming: boolean
  streamingMessage: string

  // Actions
  loadConversations: () => Promise<void>
  loadMessages: (conversationId: number) => Promise<void>
  loadModels: () => Promise<void>
  createConversation: (title: string, model: string) => Promise<Conversation>
  selectConversation: (conversation: Conversation | null) => void
  deleteConversation: (conversationId: number) => Promise<void>
  sendMessage: (
    content: string,
    params: {
      model?: string
      temperature?: number
      top_p?: number
      max_tokens?: number
    }
  ) => Promise<void>
}

const ChatContext = createContext<ChatContextType | undefined>(undefined)

export function ChatProvider({ children }: { children: ReactNode }) {
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [currentConversation, setCurrentConversation] = useState<Conversation | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [models, setModels] = useState<Model[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [isStreaming, setIsStreaming] = useState(false)
  const [streamingMessage, setStreamingMessage] = useState('')

  const loadConversations = useCallback(async () => {
    try {
      const convs = await api.getConversations()
      setConversations(convs)
    } catch (error) {
      console.error('Failed to load conversations:', error)
    }
  }, [])

  const loadMessages = useCallback(async (conversationId: number) => {
    try {
      setIsLoading(true)
      const msgs = await api.getMessages(conversationId)
      setMessages(msgs)
    } catch (error) {
      console.error('Failed to load messages:', error)
    } finally {
      setIsLoading(false)
    }
  }, [])

  const loadModels = useCallback(async () => {
    try {
      const modelList = await api.getModels()
      setModels(modelList)
    } catch (error) {
      console.error('Failed to load models:', error)
    }
  }, [])

  const createConversation = useCallback(async (title: string, model: string) => {
    try {
      const conversation = await api.createConversation(title, model)
      setConversations(prev => [conversation, ...prev])
      return conversation
    } catch (error) {
      console.error('Failed to create conversation:', error)
      throw error
    }
  }, [])

  const selectConversation = useCallback((conversation: Conversation | null) => {
    setCurrentConversation(conversation)
    if (conversation) {
      loadMessages(conversation.id)
    } else {
      setMessages([])
    }
  }, [loadMessages])

  const deleteConversation = useCallback(async (conversationId: number) => {
    try {
      await api.deleteConversation(conversationId)
      setConversations(prev => prev.filter(c => c.id !== conversationId))
      if (currentConversation?.id === conversationId) {
        setCurrentConversation(null)
        setMessages([])
      }
    } catch (error) {
      console.error('Failed to delete conversation:', error)
      throw error
    }
  }, [currentConversation])

  const sendMessage = useCallback(async (
    content: string,
    params: {
      model?: string
      temperature?: number
      top_p?: number
      max_tokens?: number
    }
  ) => {
    try {
      setIsLoading(true)
      setIsStreaming(true)
      setStreamingMessage('')

      // Add user message immediately
      const userMessage: Message = {
        id: Date.now(),
        role: 'user',
        content,
        created_at: new Date().toISOString(),
        token_count: 0
      }
      setMessages(prev => [...prev, userMessage])

      // Send to API with streaming
      await api.sendMessageStream(
        {
          conversation_id: currentConversation?.id,
          message: content,
          ...params
        },
        // On chunk
        (chunk: string) => {
          setStreamingMessage(prev => prev + chunk)
        },
        // On complete
        () => {
          setIsStreaming(false)
          // Reload messages to get the complete conversation
          if (currentConversation) {
            loadMessages(currentConversation.id)
          } else {
            // If new conversation, reload conversation list
            loadConversations()
          }
          setStreamingMessage('')
        },
        // On error
        (error: Error) => {
          console.error('Streaming error:', error)
          setIsStreaming(false)
          setStreamingMessage('')
        }
      )
    } catch (error) {
      console.error('Failed to send message:', error)
      setIsStreaming(false)
    } finally {
      setIsLoading(false)
    }
  }, [currentConversation, loadMessages, loadConversations])

  return (
    <ChatContext.Provider
      value={{
        conversations,
        currentConversation,
        messages,
        models,
        isLoading,
        isStreaming,
        streamingMessage,
        loadConversations,
        loadMessages,
        loadModels,
        createConversation,
        selectConversation,
        deleteConversation,
        sendMessage
      }}
    >
      {children}
    </ChatContext.Provider>
  )
}

export function useChat() {
  const context = useContext(ChatContext)
  if (context === undefined) {
    throw new Error('useChat must be used within a ChatProvider')
  }
  return context
}

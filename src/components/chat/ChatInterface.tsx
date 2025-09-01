import React, { useState, useEffect, useCallback, useRef } from 'react'
import { Message } from '@/types'

interface ChatInterfaceProps {
  conversationId?: string
  scenario: string
  onMessageSend?: (message: string) => void
  onConversationCreate?: (conversation: any) => void
}

export default function ChatInterface({ 
  conversationId, 
  scenario, 
  onMessageSend,
  onConversationCreate 
}: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [isTyping, setIsTyping] = useState(false)
  const [isConnected, setIsConnected] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Removed auto-scroll functionality per user request
  // Users can manually scroll as needed

  // Connect to WebSocket when conversationId changes
  useEffect(() => {
    if (!conversationId) return

    // Close existing connection
    if (wsRef.current) {
      wsRef.current.close()
    }

    // Create new WebSocket connection
    const ws = new WebSocket(`ws://localhost:8000/ws/${conversationId}`)
    wsRef.current = ws

    ws.onopen = () => {
      setIsConnected(true)
    }

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      
      switch (data.type) {
        case 'connection_established':
          break
        case 'new_message':
          setMessages(prev => [...prev, {
            ...data.message,
            role: data.message.role === 'USER' ? 'user' : data.message.role === 'ASSISTANT' ? 'assistant' : data.message.role,
            timestamp: data.message.timestamp || new Date()
          }])
          break
        case 'ai_response_start':
          setIsTyping(true)
          break
        case 'ai_response_complete':
          setIsTyping(false)
          setMessages(prev => [...prev, {
            ...data.response,
            role: data.response.role === 'ASSISTANT' ? 'assistant' : data.response.role === 'USER' ? 'user' : data.response.role,
            timestamp: data.response.timestamp || new Date()
          }])
          break
        case 'error':
          setIsTyping(false)
          setMessages(prev => [...prev, {
            id: `error-${Date.now()}`,
            role: 'assistant',
            content: data.message || "Sorry, I encountered an error. Please try again.",
            timestamp: new Date()
          }])
          break
        case 'typing_indicator':
          break
        case 'user_disconnected':
          break
        default:
          break
      }
    }

    ws.onclose = () => {
      setIsConnected(false)
    }

    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
    }
  }, [conversationId])

  const sendMessage = useCallback((message: string) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      const messageData = {
        type: 'user_message',
        content: message,
        timestamp: new Date().toISOString()
      }
      wsRef.current.send(JSON.stringify(messageData))
    }
  }, [])

  const handleSendMessage = async (message: string) => {
    try {
      if (conversationId) {
        if (isConnected) {
          // Send via WebSocket - don't add message to UI yet, wait for server broadcast
          sendMessage(message)
        } else {
          // Add user message immediately for API calls only
          const userMessage: Message = {
            id: `temp-${Date.now()}`,
            role: 'user',
            content: message,
            timestamp: new Date()
          }
          setMessages(prev => [...prev, userMessage])
          
          // Send via API if conversation exists but WebSocket not connected
          const messageResponse = await fetch(`http://localhost:8000/api/v1/conversations/${conversationId}/messages`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ content: message })
          })
          
          if (messageResponse.ok) {
            const aiMessage = await messageResponse.json()
            const aiMessageFormatted = {
              id: aiMessage.id,
              role: 'assistant' as const,
              content: aiMessage.content,
              timestamp: aiMessage.created_at || new Date()
            }
            setMessages(prev => [...prev, aiMessageFormatted])
          }
        }
      } else {
        // Add user message immediately for new conversations
        const userMessage: Message = {
          id: `temp-${Date.now()}`,
          role: 'user',
          content: message,
          timestamp: new Date()
        }
        setMessages(prev => [...prev, userMessage])
        
        // Create new conversation via API
        const response = await fetch('http://localhost:8000/api/v1/conversations/start', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            scenario_type: scenario,
            title: message.slice(0, 50) + (message.length > 50 ? '...' : '')
          })
        })

        if (response.ok) {
          const conversation = await response.json()
          onConversationCreate?.(conversation)
          
          // Send first message and get AI response
          const messageResponse = await fetch(`http://localhost:8000/api/v1/conversations/${conversation.id}/messages`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ content: message })
          })
          
          if (messageResponse.ok) {
            const aiMessage = await messageResponse.json()
            // Add AI response to UI
            const aiMessageFormatted = {
              id: aiMessage.id,
              role: 'assistant' as const,
              content: aiMessage.content,
              timestamp: aiMessage.created_at || new Date()
            }
            setMessages(prev => [...prev, aiMessageFormatted])
          }
        }
      }
      
      onMessageSend?.(message)
    } catch (error) {
      console.error('Error sending message:', error)
      // Add error message
      setMessages(prev => [...prev, {
        id: `error-${Date.now()}`,
        content: "I'm sorry, I'm having trouble connecting right now. Please try again.",
        role: 'assistant',
        timestamp: new Date()
      }])
    }
  }

  // Cleanup WebSocket on unmount
  useEffect(() => {
    return () => {
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }, [])

  return (
    <div className="flex flex-col h-full max-h-full bg-white dark:bg-gray-900 overflow-hidden">
      {/* Connection Status */}
      {conversationId && (
        <div className="flex-shrink-0 px-4 py-2 text-xs text-center border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800">
          {isConnected ? (
            <span className="inline-flex items-center text-green-600 dark:text-green-400">
              <div className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></div>
              Connected
            </span>
          ) : (
            <span className="inline-flex items-center text-amber-600 dark:text-amber-400">
              <div className="w-2 h-2 bg-amber-500 rounded-full mr-2"></div>
              Connecting...
            </span>
          )}
        </div>
      )}

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3 min-h-0 [&::-webkit-scrollbar]:hidden [-ms-overflow-style:none] [scrollbar-width:none]">
        {messages.length === 0 && (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-6 h-6 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
              </div>
              <p className="text-gray-500 dark:text-gray-400 text-sm">
                Start a conversation by typing a message below
              </p>
            </div>
          </div>
        )}

        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'} mb-4`}
          >
            <div className={`flex items-start space-x-2 max-w-[85%] sm:max-w-[75%] ${message.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
              {/* Avatar */}
              <div className={`w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center text-xs font-medium ${
                message.role === 'user'
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-300'
              }`}>
                {message.role === 'user' ? 'U' : 'AI'}
              </div>
              
              {/* Message Bubble */}
              <div className={`relative px-3 py-2 sm:px-4 sm:py-3 rounded-2xl break-words overflow-hidden ${
                message.role === 'user'
                  ? 'bg-blue-500 text-white rounded-br-md'
                  : 'bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100 rounded-bl-md'
              }`}>
                <div className="text-sm leading-relaxed whitespace-pre-wrap break-words">
                  {message.content}
                </div>
                {/* Timestamp */}
                <div className={`text-xs mt-1 ${
                  message.role === 'user' 
                    ? 'text-blue-100' 
                    : 'text-gray-500 dark:text-gray-400'
                }`}>
                  {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </div>
              </div>
            </div>
          </div>
        ))}
        
        {/* Typing Indicator */}
        {isTyping && (
          <div className="flex justify-start mb-4">
            <div className="flex items-start space-x-2 max-w-[80%]">
              <div className="w-8 h-8 rounded-full bg-gray-200 dark:bg-gray-700 flex items-center justify-center text-xs font-medium text-gray-600 dark:text-gray-300">
                AI
              </div>
              <div className="bg-gray-100 dark:bg-gray-800 rounded-2xl rounded-bl-md px-4 py-3">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
              </div>
            </div>
          </div>
        )}
        
        {/* Auto scroll anchor */}
        <div ref={messagesEndRef} />
      </div>

      {/* Message Input */}
      <div className="flex-shrink-0 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 p-3 sm:p-4">
        <form onSubmit={(e) => {
          e.preventDefault()
          const textarea = e.currentTarget.elements.namedItem('message') as HTMLTextAreaElement
          if (textarea.value.trim()) {
            handleSendMessage(textarea.value.trim())
            textarea.value = ''
            textarea.style.height = 'auto'
          }
        }}>
          <div className="flex items-end space-x-2 sm:space-x-3">
            <div className="flex-1">
              <textarea
                name="message"
                placeholder="Type your message..."
                className="w-full px-3 py-2 sm:px-4 sm:py-3 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 focus:border-transparent text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 text-sm"
                rows={1}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault()
                    const form = e.currentTarget.form
                    if (form) {
                      const formEvent = new Event('submit', { cancelable: true, bubbles: true })
                      form.dispatchEvent(formEvent)
                    }
                  }
                }}
                onInput={(e) => {
                  const target = e.target as HTMLTextAreaElement
                  target.style.height = 'auto'
                  target.style.height = Math.min(target.scrollHeight, 100) + 'px'
                }}
              />
            </div>
            <button
              type="submit"
              className="flex-shrink-0 w-9 h-9 sm:w-10 sm:h-10 bg-blue-500 hover:bg-blue-600 focus:bg-blue-600 text-white rounded-full flex items-center justify-center transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:focus:ring-offset-gray-900"
            >
              <svg className="w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
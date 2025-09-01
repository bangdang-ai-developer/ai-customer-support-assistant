'use client'

import React from 'react'
import { cn, formatTimestamp } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { ThumbsUp, ThumbsDown, Copy, User, Bot } from 'lucide-react'

export interface Message {
  id: string
  content: string
  role: 'USER' | 'ASSISTANT' | 'SYSTEM'
  timestamp: string
  tokens_used?: number
  response_time?: number
  metadata?: Record<string, any>
}

interface ChatMessageProps {
  message: Message
  onFeedback?: (messageId: string, rating: 'POSITIVE' | 'NEGATIVE') => void
  isTyping?: boolean
}

export const ChatMessage: React.FC<ChatMessageProps> = ({
  message,
  onFeedback,
  isTyping = false
}) => {
  const isUser = message.role === 'USER'
  const isAssistant = message.role === 'ASSISTANT'

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text)
    } catch (err) {
      console.error('Failed to copy text: ', err)
    }
  }

  if (isTyping) {
    return (
      <div className="flex items-start gap-3 mb-4 animate-slide-in">
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-muted flex items-center justify-center">
          <Bot className="w-4 h-4 text-muted-foreground" />
        </div>
        <div className="flex-1 max-w-[80%]">
          <div className="bg-muted rounded-lg px-4 py-3">
            <div className="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className={cn(
      "flex items-start gap-3 mb-4 animate-slide-in",
      isUser && "flex-row-reverse"
    )}>
      {/* Avatar */}
      <div className={cn(
        "flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center",
        isUser ? "bg-primary text-primary-foreground" : "bg-muted"
      )}>
        {isUser ? (
          <User className="w-4 h-4" />
        ) : (
          <Bot className="w-4 h-4 text-muted-foreground" />
        )}
      </div>

      {/* Message Content */}
      <div className={cn(
        "flex-1 max-w-[80%]",
        isUser && "flex flex-col items-end"
      )}>
        <div className={cn(
          "rounded-lg px-4 py-3 relative group",
          isUser ? "bg-primary text-primary-foreground ml-auto" : "bg-muted"
        )}>
          <div className="whitespace-pre-wrap text-sm leading-relaxed">
            {message.content}
          </div>
          
          {/* Message metadata for assistant messages */}
          {isAssistant && message.metadata && (
            <div className="mt-2 pt-2 border-t border-border/20 text-xs text-muted-foreground flex items-center gap-2">
              {message.metadata.model && (
                <span className="bg-background/10 px-2 py-1 rounded">
                  {message.metadata.model}
                </span>
              )}
              {message.response_time && (
                <span>{message.response_time}ms</span>
              )}
              {message.tokens_used && (
                <span>{message.tokens_used} tokens</span>
              )}
            </div>
          )}
        </div>

        {/* Timestamp and Actions */}
        <div className={cn(
          "flex items-center gap-2 mt-1 text-xs text-muted-foreground",
          isUser && "flex-row-reverse"
        )}>
          <span>{formatTimestamp(new Date(message.timestamp))}</span>
          
          {/* Action buttons (show on hover) */}
          <div className="opacity-0 group-hover:opacity-100 transition-opacity flex items-center gap-1">
            <Button
              variant="ghost"
              size="sm"
              className="h-6 w-6 p-0"
              onClick={() => copyToClipboard(message.content)}
            >
              <Copy className="w-3 h-3" />
            </Button>
            
            {/* Feedback buttons for assistant messages */}
            {isAssistant && onFeedback && (
              <>
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-6 w-6 p-0 text-green-600 hover:text-green-700"
                  onClick={() => onFeedback(message.id, 'POSITIVE')}
                >
                  <ThumbsUp className="w-3 h-3" />
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-6 w-6 p-0 text-red-600 hover:text-red-700"
                  onClick={() => onFeedback(message.id, 'NEGATIVE')}
                >
                  <ThumbsDown className="w-3 h-3" />
                </Button>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default ChatMessage
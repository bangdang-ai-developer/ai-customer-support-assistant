// TypeScript type definitions exports

export interface Message {
  id: string
  content: string
  role: 'user' | 'assistant' | 'system'
  timestamp: Date
  tokens_used?: number
  response_time?: number
  metadata?: Record<string, any>
}

export type ScenarioType = 'ECOMMERCE' | 'SAAS' | 'SERVICE_BUSINESS'

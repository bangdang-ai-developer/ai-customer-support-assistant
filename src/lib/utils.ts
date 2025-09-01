import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatTimestamp(date: Date): string {
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const seconds = Math.floor(diff / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)

  if (days > 0) {
    return `${days}d ago`
  }
  if (hours > 0) {
    return `${hours}h ago`
  }
  if (minutes > 0) {
    return `${minutes}m ago`
  }
  return "just now"
}

export function generateConversationTitle(firstMessage: string): string {
  // Extract first few words as conversation title
  const words = firstMessage.split(' ').slice(0, 6)
  let title = words.join(' ')
  if (firstMessage.split(' ').length > 6) {
    title += '...'
  }
  return title || 'New Conversation'
}
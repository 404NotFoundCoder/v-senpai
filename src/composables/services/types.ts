// ✅ types.ts - 放共同使用的型別
export interface Reference {
  id: string
  source: string
  content: string
}

export interface ChatMessage {
  sender: string
  text: string
  createdAt: string
  metadata?: string
  references?: Reference[]
  docid?: string
  feedback?: string
  userText?: string
  chatHistory?: Array<{
    aiText: string
    userText: string
    metadata: string
  }>
}

export interface ChatPair {
  user: string
  ai: string
  metadata: string
  references?: Reference[]
}

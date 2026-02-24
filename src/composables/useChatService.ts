// ✅ useChatService.ts - 主邏輯整合點
import { ref, type Ref } from 'vue'
import { auth } from '@/config/firebaseConfig'
import type { ChatMessage, ChatPair } from './services/types'
import { fetchChatHistory } from './services/chatHistoryService'
import { saveConversationToFirestore } from './services/chatFirestoreService'
import { readUserAccessToken } from './services/userService'

export function useChatService(
  messages: Ref<ChatMessage[]>,
  input: Ref<string>,
  isThinking: Ref<boolean>,
) {
  const accessToken = ref('')
  const messagePairs = ref<ChatPair[]>([])

  const handleSuggestedQuestion = (question: string) => {
    input.value = question
    sendMessage()
  }

  const sendMessage = async () => {
    const userText = input.value.trim()
    const uid = auth.currentUser?.uid
    if (!userText || !accessToken.value || !uid) return

    const timestamp = new Date().toISOString()
    messages.value.push({ sender: 'user', text: userText, createdAt: timestamp })
    input.value = ''
    isThinking.value = true

    try {
      const history = await fetchChatHistory(uid)
      if (!history || history.length === 0) {
        console.warn('⚠️ 沒有找到歷史對話，將使用空陣列')
      }
      //deploy
      // const response = await fetch(`/api/chat`, {
      const response = await fetch(`http://localhost:5000/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userText,
          history: history,
          accessToken: accessToken.value,
        }),
        mode: 'cors',
      })

      if (!response.ok) throw new Error(`HTTP 錯誤！狀態碼: ${response.status}`)

      const data = await response.json()
      const aiText = data.answer
      const metadata = data.context
      console.log(data)

      messages.value[messages.value.length - 1] = {
        sender: 'ai',
        text: aiText,
        createdAt: new Date().toISOString(),
      }

      messagePairs.value.push({ user: userText, ai: aiText, metadata })
      await saveConversationToFirestore(uid, messagePairs.value)
      // await saveChatHistoryToRTDB(uid, [...history, ...messagePairs.value])
      messagePairs.value = []
    } catch (err: any) {
      console.error('❌API打失敗:', err)
      messages.value.push({
        sender: 'ai',
        text: '⚠️ 系統錯誤，請稍後再試\n' + (err?.message ?? ''),
        createdAt: new Date().toISOString(),
      })
    } finally {
      isThinking.value = false
    }
  }

  const readUserData = async (uid: string) => {
    const token = await readUserAccessToken(uid)
    if (token) accessToken.value = token
  }

  return {
    accessToken,
    sendMessage,
    handleSuggestedQuestion,
    readUserData,
  }
}

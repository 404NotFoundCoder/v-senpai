// ✅ chatFirestoreService.ts - Firestore 對話紀錄操作
import {
  collection,
  doc,
  getDocs,
  onSnapshot,
  orderBy,
  query,
  serverTimestamp,
  addDoc,
  setDoc,
} from 'firebase/firestore'
import { db } from '@/config/firebaseConfig'
import type { ChatPair, ChatMessage } from './types'
import type { Ref } from 'vue'
import { formatChatTimestamp } from '@/utils/dateTime'

export const saveConversationToFirestore = async (uid: string, pairs: ChatPair[]) => {
  try {
    await addDoc(collection(db, `/users/${uid}/conversation-0610`), {
      messagePairs: pairs,
      createdAt: serverTimestamp(),
    })
  } catch (e) {
    console.error('❌對話儲存失敗', e)
  }
}

export const fetchChatHistoryFromFirestore = async (uid: string): Promise<ChatPair[]> => {
  try {
    const convoRef = collection(db, `users/${uid}/conversation-0610`)
    const q = query(convoRef, orderBy('createdAt', 'asc'))
    const snapshot = await getDocs(q)
    const pairs: ChatPair[] = []

    for (const doc of snapshot.docs) {
      const data = doc.data()
      if (Array.isArray(data.messagePairs)) {
        data.messagePairs.forEach((pair: any) => {
          pairs.push({
            user: pair.user,
            ai: pair.ai,
            metadata: pair.metadata ?? '',
            references: Array.isArray(pair.references) ? pair.references : undefined,
          })
        })
      }
    }
    console.log('✅ Firestore 讀取成功:', pairs)

    return pairs
  } catch (e) {
    console.error('❌ Firestore 讀取失敗:', e)
    return []
  }
}

export const watchFirestoreMessages = (
  uid: string,
  messages: Ref<ChatMessage[]>,
  defaultMessage: ChatMessage,
) => {
  const convoRef = collection(db, `/users/${uid}/conversation-0610`)
  const q = query(convoRef, orderBy('createdAt'))

  onSnapshot(q, (snapshot) => {
    const loadedMessages: ChatMessage[] = []
    const rollingPairs: Array<{ user: string; ai: string; metadata: string }> = []
    snapshot.forEach((docSnap) => {
      const data = docSnap.data() as {
        messagePairs: ChatPair[]
        createdAt?: any
        feedback?: string
      }

      const timestamp = formatChatTimestamp(data.createdAt?.toDate?.() ?? new Date())

      data.messagePairs.forEach((pair) => {
        loadedMessages.push({
          docid: docSnap.id,
          sender: 'user',
          text: pair.user,
          createdAt: timestamp,
        })
        const chatHistory = rollingPairs.slice(Math.max(0, rollingPairs.length - 3)).map((item) => ({
          aiText: item.ai,
          userText: item.user,
          metadata: item.metadata || '',
        }))
        loadedMessages.push({
          docid: docSnap.id,
          sender: 'ai',
          text: pair.ai,
          createdAt: timestamp,
          userText: pair.user,
          metadata: pair.metadata,
          references: Array.isArray(pair.references) ? pair.references : undefined,
          feedback: data.feedback ?? undefined,
          chatHistory,
        })
        rollingPairs.push({
          user: pair.user,
          ai: pair.ai,
          metadata: pair.metadata ?? '',
        })
      })
    })

    if (messages.value.length === 0) messages.value.push(defaultMessage)
    // messages.value.push(...loadedMessages)
    messages.value = [defaultMessage, ...loadedMessages]
  })
  console.log(messages.value)
}

export async function updateMessageFeedback(
  userId: string,
  messageId: string,
  type: 'like' | 'dislike',
  context?: {
    userText?: string
    aiText?: string
    metadata?: string
    chatHistory?: Array<{ aiText: string; userText: string; metadata: string }>
  },
): Promise<void> {
  // 1. 保存到用户自己的collection（原有功能）
  const messageRef = doc(db, `users/${userId}/conversation-${type}/${messageId}`)

  await setDoc(messageRef, {
    feedbackAt: serverTimestamp(),
  })

  // 2. 從 Firestore 讀取完整對話資訊並保存到公共 collection
  try {
    if (context?.userText && context?.aiText) {
      const collectionName = `public-feedback-${type}`
      const feedbackRef = doc(db, collectionName, messageId)
      await setDoc(feedbackRef, {
        uid: userId,
        aiText: context.aiText,
        userText: context.userText,
        metadata: context.metadata || '',
        chatHistory: Array.isArray(context.chatHistory) ? context.chatHistory.slice(-3) : [],
        createdAt: serverTimestamp(),
      })
      console.log(`✅ 回饋已保存到公共 collection: public-feedback-${type}/${messageId}`)
      return
    }

    // fallback：若前端未帶 context，才從 Firestore 補查
    const convoRef = collection(db, `users/${userId}/conversation-0610`)
    const q = query(convoRef, orderBy('createdAt', 'asc'))
    const snapshot = await getDocs(q)

    const allPairs: Array<{ docId: string; user: string; ai: string; metadata: string }> = []

    snapshot.forEach((docSnap) => {
      const data = docSnap.data()
      const messagePairs = Array.isArray(data.messagePairs) ? data.messagePairs : []

      messagePairs.forEach((pair: any) => {
        if (pair?.user && pair?.ai) {
          allPairs.push({
            docId: docSnap.id,
            user: pair.user,
            ai: pair.ai,
            metadata: pair.metadata || '',
          })
        }
      })
    })

    const currentIndex = allPairs.findIndex((pair) => pair.docId === messageId)
    if (currentIndex === -1) {
      console.warn('⚠️ 找不到對應回饋的對話紀錄:', messageId)
      return
    }

    const currentPair = allPairs[currentIndex]
    const chatHistory = allPairs
      .slice(Math.max(0, currentIndex - 3), currentIndex)
      .map((pair) => ({
        aiText: pair.ai,
        userText: pair.user,
        metadata: pair.metadata || '',
      }))

    const collectionName = `public-feedback-${type}`
    const feedbackRef = doc(db, collectionName, messageId)
    await setDoc(feedbackRef, {
      uid: userId,
      aiText: currentPair.ai,
      userText: currentPair.user,
      metadata: currentPair.metadata || '',
      chatHistory,
      createdAt: serverTimestamp(),
    })

      console.log(`✅ 回饋已保存到公共 collection: public-feedback-${type}/${messageId}`)
  } catch (error) {
    console.error('❌ 保存回饋到公共 collection 失敗:', error)
    // 不拋出錯誤，因為使用者自己的回饋已經保存成功
  }
}

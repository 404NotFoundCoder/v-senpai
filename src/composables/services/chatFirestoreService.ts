// ✅ chatFirestoreService.ts - Firestore 對話紀錄操作
import {
  collection,
  doc,
  getDoc,
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
    const convoRef = collection(db, `users/${uid}/conversation`)
    const q = query(convoRef, orderBy('createdAt', 'asc'))
    const snapshot = await getDocs(q)
    const pairs: ChatPair[] = []

    for (const doc of snapshot.docs) {
      const data = doc.data()
      if (Array.isArray(data.messagePairs)) {
        data.messagePairs.forEach((pair: any) => {
          pairs.push({ user: pair.user, ai: pair.ai, metadata: pair.metadata })
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
    snapshot.forEach((docSnap) => {
      const data = docSnap.data() as {
        messagePairs: ChatPair[]
        createdAt?: any
        feedback?: string
      }

      const timestamp =
        data.createdAt?.toDate?.()?.toLocaleString?.() ?? new Date().toLocaleString()

      data.messagePairs.forEach((pair) => {
        loadedMessages.push({
          docid: docSnap.id,
          sender: 'user',
          text: pair.user,
          createdAt: timestamp,
        })
        loadedMessages.push({
          docid: docSnap.id,
          sender: 'ai',
          text: pair.ai,
          createdAt: timestamp,
          metadata: pair.metadata,
          feedback: data.feedback ?? undefined,
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
): Promise<void> {
  // 1. 保存到用户自己的collection（原有功能）
  const messageRef = doc(db, `users/${userId}/conversation-${type}/${messageId}`)

  await setDoc(messageRef, {
    feedbackAt: serverTimestamp(),
  })

  // 2. 從 Firestore 讀取完整對話資訊並保存到公共 collection
  try {
    const conversationRef = doc(db, `users/${userId}/conversation-0610`, messageId)
    const conversationSnap = await getDoc(conversationRef)

    if (conversationSnap.exists()) {
      const data = conversationSnap.data()
      const messagePairs = data.messagePairs || []

      // 遍歷所有對話對，保存到公共 collection
      // 路徑: public-feedback-like/${messageId} 或 public-feedback-dislike/${messageId}
      for (const pair of messagePairs) {
        if (pair.user && pair.ai) {
          const collectionName = `public-feedback-${type}` // 'public-feedback-like' 或 'public-feedback-dislike'
          const feedbackRef = doc(db, collectionName, messageId)
          await setDoc(feedbackRef, {
            uid: userId,
            aiText: pair.ai,
            userText: pair.user,
            metadata: pair.metadata || '',
            createdAt: serverTimestamp(),
          })
        }
      }
      console.log(`✅ 回饋已保存到公共 collection: public-feedback-${type}/${messageId}`)
    } else {
      console.warn('⚠️ 找不到對話紀錄:', messageId)
    }
  } catch (error) {
    console.error('❌ 保存回饋到公共 collection 失敗:', error)
    // 不拋出錯誤，因為使用者自己的回饋已經保存成功
  }
}

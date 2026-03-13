<template>
  <div class="flex my-5" :class="isSelf ? 'justify-end' : 'justify-start'">
    <div class="flex flex-col" :class="isSelf ? 'items-end' : 'items-start'">
      <div
        class="max-w-md px-4 py-2 rounded-2xl shadow-md whitespace-pre-wrap break-words"
        :class="
          isSelf
            ? 'bg-primary-500 text-white rounded-br-none'
            : 'bg-primary-100 text-primary-800 rounded-bl-none'
        "
      >
        {{ text }}
      </div>

      <span class="text-xs text-gray-400 mt-1" v-if="timestamp">{{ timestamp }}</span>

      <!-- 回饋區塊（僅非自己訊息顯示） -->
      <div v-if="!isSelf" class="mt-2">
        <div v-if="!feedbackGiven">
          <div class="flex gap-3">
            <!-- 主控按鈕 -->
            <button
              class="text-xs text-primary-800 bg-primary-200 hover:bg-primary-100 transition rounded-full px-3 py-1 shadow-sm"
              @click="showMetadataDialog = true"
            >
              原文
            </button>

            <button
              class="text-xs text-primary-600 bg-primary-100 hover:bg-primary-200 transition rounded-full px-3 py-1 shadow-sm"
              @click="showFeedback = !showFeedback"
            >
              {{ showFeedback ? '收合回饋' : '給予回饋' }}
            </button>
          </div>

          <!-- 展開回饋 -->
          <div v-if="showFeedback" class="mt-2 flex gap-3 animate-fade-in">
            <button
              class="bg-white border border-green-200 hover:border-green-400 text-green-600 px-3 py-1 rounded-full shadow-sm hover:shadow transition"
              @click="sendFeedback('like')"
            >
              <i class="fi fi-rr-social-network"></i>
            </button>
            <button
              class="bg-white border border-red-200 hover:border-red-400 text-red-500 px-3 py-1 rounded-full shadow-sm hover:shadow transition"
              @click="sendFeedback('dislike')"
            >
              <i class="fi fi-rr-hand"></i>
            </button>
          </div>
        </div>

        <!-- 感謝訊息 -->
        <!-- <div v-else class="text-xs text-green-600 mt-2">✅ 已收到你的回饋，感謝！</div> -->
        <div v-if="feedbackGiven">✅ 已收到你的回饋，感謝！</div>
      </div>
    </div>
  </div>

  <!-- 原文 / References Dialog -->
  <div v-if="showMetadataDialog" class="reference-overlay" @click.self="showMetadataDialog = false">
    <div class="reference-dialog">
      <h2 class="reference-title">參考原文</h2>

      <div class="reference-body">
        <template v-if="referencesList.length">
          <div v-for="(ref, i) in referencesList" :key="ref.id + String(i)" class="reference-item">
            <a
              :href="refLink(ref.id)"
              target="_blank"
              rel="noopener noreferrer"
              class="reference-link"
            >
              <span class="reference-link-emoji" aria-hidden="true">🔗</span>
              <span class="reference-link-text">{{ ref.source || '（無標題）' }}</span>
            </a>
            <div class="reference-content">{{ ref.content || '（無內文）' }}</div>
          </div>
        </template>

        <template v-else>
          <pre class="reference-fallback">{{ props.metadata || '（無原文說明）' }}</pre>
        </template>
      </div>

      <div class="reference-actions">
        <button type="button" class="reference-close" @click="showMetadataDialog = false">
          關閉
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useFeedback } from '@/composables/useFeedback'
import { getAuth } from 'firebase/auth'
import { computed } from 'vue'
import MarkdownIt from 'markdown-it'

const md = new MarkdownIt()

export interface ReferenceItem {
  id: string
  source: string
  content: string
}

const props = defineProps<{
  text: string
  isSelf?: boolean
  timestamp?: string
  metadata?: string
  references?: ReferenceItem[]
  docid?: string
}>()

const BASE_POST_URL = 'http://localhost:3000/post'
const refLink = (id: string) => `${BASE_POST_URL}/${id}`

const referencesList = computed(() => {
  const r = props.references
  if (!Array.isArray(r) || r.length === 0) return []
  return r.map((item) => ({
    id: item?.id ?? '',
    source: item?.source ?? '',
    content: item?.content ?? '',
  }))
})

const renderedText = computed(() => md.render(props.text || ''))

const { showFeedback, feedbackGiven, showMetadataDialog, toggleFeedback, giveFeedback } =
  useFeedback()

const userId = getAuth().currentUser?.uid || '' // 確保已登入

async function sendFeedback(type: 'like' | 'dislike') {
  if (!props.docid || !userId) return

  // 如果是 dislike，調用 draft API
  if (type === 'dislike') {
    await callDraftAPI()
  }

  giveFeedback(userId, props.docid, type)
  alert(type === 'like' ? '感謝你的讚！我們會持續努力！' : '感謝你的回饋，我們會努力改進！')
}

// 調用 draft API
async function callDraftAPI() {
  try {
    // 獲取使用者訊息
    const auth = getAuth()
    const user = auth.currentUser
    if (!user) {
      console.error('使用者未登入')
      return
    }

    // 從 Firebase 讀取歷史紀錄
    const {
      collection,
      query,
      getDocs,
      orderBy: firestoreOrderBy,
    } = await import('firebase/firestore')
    const { db } = await import('@/config/firebaseConfig')

    const conversationRef = collection(db, `users/${user.uid}/conversation-0610`)
    const q = query(conversationRef, firestoreOrderBy('createdAt', 'asc'))
    const snapshot = await getDocs(q)

    // 收集所有對話
    const allHistory: Array<{ user: string; ai: string; docId: string }> = []
    snapshot.forEach((doc) => {
      const data = doc.data()
      const messagePairs = data.messagePairs || []
      messagePairs.forEach((pair: any) => {
        if (pair.user && pair.ai) {
          allHistory.push({
            user: pair.user,
            ai: pair.ai,
            docId: doc.id,
          })
        }
      })
    })

    // 找到目前 docid 的位置
    const currentDocId = props.docid
    const currentIndex = allHistory.findIndex((item) => item.docId === currentDocId)

    if (currentIndex === -1) {
      console.warn('找不到目前對話紀錄')
      return
    }

    // 取得前 3 個對話對（不包含目前的）
    const history = allHistory.slice(Math.max(0, currentIndex - 3), currentIndex)

    // 目前問題就是目前對話對中的 user 問題
    const finalQuestion = allHistory[currentIndex].user

    console.log('呼叫 draft API:', {
      history: history.map((h) => ({ user: h.user, ai: h.ai })),
      finalQuestion,
    })

    // 從 Firestore 讀取 access token
    const { readUserAccessToken } = await import('@/composables/services/userService')
    const accessToken = await readUserAccessToken(user.uid)

    if (!accessToken) {
      console.error('找不到 access token')
      return
    }

    // 呼叫 draft API
    const response = await fetch('http://localhost:5000/api/draft', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        accessToken: accessToken,
        history: history.map((h) => ({ user: h.user, ai: h.ai })),
        finalQuestion: finalQuestion,
      }),
      mode: 'cors',
    })

    if (!response.ok) {
      throw new Error(`HTTP 錯誤！狀態碼: ${response.status}`)
    }

    const data = await response.json()

    console.log('✅ Draft API 回應:', data)

    // 正規化 draft：若後端回傳的是字串（JSON 字串），先解析成物件
    let draft = data.draft
    if (typeof draft === 'string') {
      try {
        draft = JSON.parse(draft)
      } catch (e) {
        console.warn('draft 是字串但無法解析為 JSON:', draft?.slice?.(0, 100))
        draft = null
      }
    }
    if (draft && typeof draft === 'object' && draft !== null) {
      console.log('Draft 內容 (物件):', draft)
      console.log('Draft title:', draft.title)
      // 可安全使用 draft.title, draft.post 等
    } else {
      console.warn('draft 不是預期的物件:', draft)
    }
    const url = new URL('http://localhost:5173/chat')
    console.log('Draft 內容:', draft)
    url.searchParams.append('title', encodeURIComponent(draft.title))
    url.searchParams.append('post', encodeURIComponent(draft.post))

    window.location.href = url.toString()
    // alert(`草稿文章已生成：\n${data.draft}`)
  } catch (error) {
    console.error('❌ 呼叫 draft API 失敗:', error)
  }
}
</script>

<style scoped>
@keyframes fade-in {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}
.animate-fade-in {
  animation: fade-in 0.2s ease-out;
}

/* 參考原文彈窗：質感版，配色符合 primary 設計 */
.reference-overlay {
  position: fixed;
  inset: 0;
  background: rgba(63, 40, 37, 0.25);
  backdrop-filter: blur(6px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 50;
  padding: 1.25rem;
}
.reference-dialog {
  background: #fff;
  border-radius: 1rem;
  box-shadow:
    0 25px 50px -12px rgba(63, 40, 37, 0.12),
    0 0 0 1px rgba(0, 0, 0, 0.06);
  max-width: 32rem;
  width: 100%;
  max-height: 80vh;
  padding: 1.5rem;
  overflow-y: auto;
  animation: reference-dialog-in 0.25s ease-out;
}
@keyframes reference-dialog-in {
  from {
    opacity: 0;
    transform: scale(0.96) translateY(-8px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}
.reference-title {
  font-size: 1.125rem;
  font-weight: 900;
  color: #654039;
  margin: 0 0 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid rgba(167, 111, 101, 0.2);
  letter-spacing: 0.02em;
}
.reference-body {
  background: #fdf7f0;
  border-radius: 0.5rem;
  padding: 1rem 1.25rem;
}
.reference-item {
  padding: 0.75rem 0;
}
.reference-item:not(:last-child) {
  border-bottom: 1px solid rgba(201, 146, 136, 0.25);
}
.reference-link {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: #a76f65;
  font-weight: 600;
  font-size: 0.9375rem;
  text-decoration: none;
  cursor: pointer;
  margin-bottom: 0.5rem;
  transition: color 0.2s ease;
}
.reference-link:hover {
  color: #87564d;
}
.reference-link-emoji {
  font-size: 1rem;
  line-height: 1;
  opacity: 0.9;
}
.reference-link-text {
  border-bottom: 1px solid transparent;
  transition: border-color 0.2s ease;
}
.reference-link:hover .reference-link-text {
  border-bottom-color: #c79288;
}
.reference-content {
  font-size: 0.875rem;
  line-height: 1.65;
  color: #654039;
  white-space: pre-wrap;
  word-break: break-word;
  background: transparent;
  padding: 0;
}
.reference-fallback {
  font-size: 0.875rem;
  color: #654039;
  white-space: pre-wrap;
  word-break: break-word;
  font-family: inherit;
  line-height: 1.6;
  margin: 0;
}
.reference-actions {
  margin-top: 1.25rem;
  text-align: right;
}
.reference-close {
  padding: 0.5rem 1.25rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: #fff;
  background: #a76f65;
  border: none;
  border-radius: 0.5rem;
  box-shadow: 0 1px 2px rgba(63, 40, 37, 0.1);
  cursor: pointer;
  transition:
    background 0.2s ease,
    box-shadow 0.2s ease;
}
.reference-close:hover {
  background: #87564d;
  box-shadow: 0 2px 4px rgba(63, 40, 37, 0.15);
}
</style>

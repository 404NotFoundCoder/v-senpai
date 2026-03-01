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

  <!-- Metadata Dialog -->
  <div
    v-if="showMetadataDialog"
    class="fixed inset-0 bg-black/30 backdrop-blur-sm flex items-center justify-center z-50 p-5"
    @click.self="showMetadataDialog = false"
  >
    <div
      class="bg-white rounded-lg shadow-xl max-w-xl w-full max-h-[80vh] p-6 animate-fade-in overflow-y-scroll"
    >
      <h2 class="text-lg font-semibold mb-3 text-primary-800 border-b pb-2">原始內容</h2>
      <pre
        class="text-sm text-primary-700 whitespace-pre-wrap break-words font-mono leading-relaxed"
        >{{ props.metadata || '（無原文說明）' }}
      </pre>
      <div class="text-right mt-4">
        <button
          class="px-4 py-2 text-sm font-medium text-white bg-red-500 rounded-md shadow hover:bg-red-600 transition"
          @click="showMetadataDialog = false"
        >
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

const props = defineProps<{
  text: string
  isSelf?: boolean
  timestamp?: string
  metadata?: string
  docid?: string
}>()

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
    const url = new URL('http://localhost:3000/create')
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
</style>

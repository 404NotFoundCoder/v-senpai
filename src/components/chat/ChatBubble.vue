<template>
  <div class="flex my-5" :class="isSelf ? 'justify-end' : 'justify-start'">
    <div class="flex flex-col" :class="isSelf ? 'items-end' : 'items-start'">
      <div
        class="max-w-md px-4 py-2 rounded-2xl shadow-md break-words chat-bubble-inner"
        :class="
          isSelf
            ? 'bg-primary-500 text-white rounded-br-none'
            : 'bg-primary-100 text-primary-800 rounded-bl-none'
        "
      >
        <div class="chat-markdown" v-html="renderedText"></div>
      </div>

      <span class="text-xs text-gray-400 mt-1" v-if="formattedTimestamp">{{
        formattedTimestamp
      }}</span>

      <!-- 回饋區塊（僅非自己訊息顯示） -->
      <div v-if="!isSelf" class="mt-2">
        <div v-if="!feedbackGiven">
          <div class="flex gap-3">
            <!-- 主控按鈕 -->
            <button
              class="text-xs text-primary-800 bg-primary-200 hover:bg-primary-100 transition rounded-full px-3 py-1 shadow-sm"
              @click="showMetadataDialog = true"
            >
              參考資料
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
      <h2 class="reference-title">參考資料</h2>

      <div class="reference-body">
        <template v-if="referencesList.length">
          <div v-for="(ref, i) in referencesList" :key="ref.id + String(i)" class="reference-item">
            <a :href="refLink(ref.id)" class="reference-link" @click.prevent="openRefPost(ref.id)">
              <span class="reference-link-emoji" aria-hidden="true">🔗</span>
              <span class="reference-link-text">{{ ref.source || '（無標題）' }}</span>
            </a>
            <div class="reference-content">{{ ref.content || '（無內文）' }}</div>
          </div>
        </template>

        <template v-else>
          <pre class="reference-fallback">{{
            props.metadata || '（無參考資料，可使用不滿意論壇求助功能）'
          }}</pre>
        </template>
      </div>

      <div class="reference-actions">
        <button type="button" class="reference-close" @click="showMetadataDialog = false">
          關閉
        </button>
      </div>
    </div>
  </div>

  <!-- 不滿意回饋：詢問是否前往論壇發問 -->
  <Teleport to="body">
    <Transition name="fade">
      <div v-if="showDislikeFollowUp" class="dislike-followup-overlay">
        <div class="dislike-followup-dialog">
          <p class="dislike-followup-text">已收到你的回饋！</p>
          <p class="dislike-followup-question">要我們幫你生成草稿文章，前往論壇發問嗎？</p>
          <div class="dislike-followup-actions">
            <button type="button" class="btn-generate" @click="handleGenerateDraft">
              要，幫我生成
            </button>
            <button type="button" class="btn-skip" @click="handleSkipDraft">不用了</button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>

  <!-- 生成草稿時的 Loading 遮罩 -->
  <Teleport to="body">
    <Transition name="fade">
      <div v-if="isDraftLoading" class="draft-loading-overlay">
        <div class="draft-loading-content">
          <div class="draft-loading-spinner"></div>
          <p class="draft-loading-text">正在為你生成草稿，請稍候...</p>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { useFeedback } from '@/composables/useFeedback'
import { useToast } from '@/composables/useToast'
import { formatChatTimestamp } from '@/utils/dateTime'
import { buildForumUrl, goForum } from '@/utils/forumAuth'
import { getAuth } from 'firebase/auth'
import { computed, ref } from 'vue'
import MarkdownIt from 'markdown-it'

const md = new MarkdownIt({ linkify: true })

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

// const BASE_POST_URL = 'http://localhost:3000/post'
const BASE_POST_URL = 'http://sa-forum.vercel.app/post'
const refLink = (id: string) => `${BASE_POST_URL}/${id}`

async function openRefPost(id: string) {
  try {
    await goForum(`/post/${id}`)
  } catch (error) {
    console.error('前往論壇文章失敗:', error)
    showToast('前往論壇失敗，請稍後再試', 'info')
  }
}

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

const formattedTimestamp = computed(() => {
  return formatChatTimestamp(props.timestamp)
})

const { showFeedback, feedbackGiven, showMetadataDialog, toggleFeedback, giveFeedback } =
  useFeedback()
const { showToast } = useToast()

const userId = getAuth().currentUser?.uid || '' // 確保已登入

const showDislikeFollowUp = ref(false)
const isDraftLoading = ref(false)

async function sendFeedback(type: 'like' | 'dislike') {
  if (!props.docid || !userId) return

  giveFeedback(userId, props.docid, type)

  if (type === 'like') {
    showToast('感謝你的讚！我們會持續努力！')
    return
  }

  // 不滿意：直接顯示詢問是否前往論壇的對話框
  showDislikeFollowUp.value = true
}

function handleSkipDraft() {
  showDislikeFollowUp.value = false
  showToast('感謝你的回饋！')
}

async function handleGenerateDraft() {
  showDislikeFollowUp.value = false
  isDraftLoading.value = true
  try {
    await callDraftAPI()
    // 成功會 redirect，不需手動關閉 loading
  } catch {
    showToast('生成失敗，請稍後再試')
  } finally {
    isDraftLoading.value = false
  }
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
    // const response = await fetch('http://localhost:5000/api/draft', {
    const response = await fetch('/api/draft', {
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
    if (!draft || typeof draft !== 'object') {
      console.warn('draft 不是預期的物件:', draft)
      throw new Error('無法解析草稿內容')
    }
    const forumUrl = await buildForumUrl('/create', {
      title: draft.title ?? '',
      post: draft.post ?? '',
    })
    window.location.href = forumUrl
  } catch (error) {
    console.error('❌ 呼叫 draft API 失敗:', error)
    throw error
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

/* Markdown 訊息樣式（繼承父層顏色以適應 user/AI 氣泡） */
.chat-markdown :deep(p) {
  margin: 0 0 0.5em;
}
.chat-markdown :deep(p:last-child) {
  margin-bottom: 0;
}
.chat-markdown :deep(h1),
.chat-markdown :deep(h2),
.chat-markdown :deep(h3) {
  margin: 0.75em 0 0.35em;
  font-weight: 700;
  line-height: 1.3;
}
.chat-markdown :deep(h1) {
  font-size: 1.1em;
}
.chat-markdown :deep(h2) {
  font-size: 1.05em;
}
.chat-markdown :deep(h3) {
  font-size: 1em;
}
.chat-markdown :deep(ul),
.chat-markdown :deep(ol) {
  margin: 0.5em 0;
  padding-left: 1.25em;
}
.chat-markdown :deep(li) {
  margin: 0.2em 0;
}
.chat-markdown :deep(code) {
  font-family: ui-monospace, monospace;
  font-size: 0.9em;
  padding: 0.15em 0.35em;
  border-radius: 0.25em;
  background: rgba(0, 0, 0, 0.08);
}
.chat-bubble-inner.bg-primary-500 .chat-markdown :deep(code) {
  background: rgba(255, 255, 255, 0.2);
}
.chat-markdown :deep(pre) {
  margin: 0.5em 0;
  padding: 0.75em 1em;
  border-radius: 0.5em;
  overflow-x: auto;
  background: rgba(0, 0, 0, 0.06);
}
.chat-bubble-inner.bg-primary-500 .chat-markdown :deep(pre) {
  background: rgba(255, 255, 255, 0.15);
}
.chat-markdown :deep(pre code) {
  padding: 0;
  background: none;
}
.chat-markdown :deep(blockquote) {
  margin: 0.5em 0;
  padding-left: 1em;
  border-left: 3px solid currentColor;
  opacity: 0.9;
}
.chat-markdown :deep(a) {
  color: inherit;
  text-decoration: underline;
  text-underline-offset: 0.15em;
}
.chat-markdown :deep(a:hover) {
  opacity: 0.85;
}
.chat-markdown :deep(hr) {
  margin: 0.75em 0;
  border: none;
  border-top: 1px solid currentColor;
  opacity: 0.4;
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

/* 不滿意回饋：詢問前往論壇的 dialog */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
.dislike-followup-overlay {
  position: fixed;
  inset: 0;
  background: rgba(63, 40, 37, 0.3);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9998;
  padding: 1rem;
}
.dislike-followup-dialog {
  background: #fff;
  border-radius: 1rem;
  padding: 1.5rem 1.75rem;
  max-width: 20rem;
  width: 100%;
  box-shadow:
    0 20px 40px rgba(63, 40, 37, 0.15),
    0 0 0 1px rgba(201, 146, 136, 0.2);
}
.dislike-followup-text {
  font-size: 1rem;
  font-weight: 600;
  color: #654039;
  margin: 0 0 0.5rem;
}
.dislike-followup-question {
  font-size: 0.9375rem;
  color: #654039;
  line-height: 1.5;
  margin: 0 0 1.25rem;
}
.dislike-followup-actions {
  display: flex;
  gap: 0.75rem;
}
.btn-generate {
  flex: 1;
  padding: 0.6rem 1rem;
  font-size: 0.9375rem;
  font-weight: 600;
  color: #fff;
  background: #a76f65;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: background 0.2s;
}
.btn-generate:hover {
  background: #87564d;
}
.btn-skip {
  padding: 0.6rem 1rem;
  font-size: 0.9375rem;
  font-weight: 500;
  color: #654039;
  background: #fbecdc;
  border: 1px solid rgba(201, 146, 136, 0.4);
  border-radius: 0.5rem;
  cursor: pointer;
  transition:
    background 0.2s,
    border-color 0.2s;
}
.btn-skip:hover {
  background: #f9d8c1;
}

/* 生成草稿 Loading 遮罩 */
.draft-loading-overlay {
  position: fixed;
  inset: 0;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(6px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}
.draft-loading-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}
.draft-loading-spinner {
  width: 2.5rem;
  height: 2.5rem;
  border: 3px solid #fbecdc;
  border-top-color: #a76f65;
  border-radius: 50%;
  animation: draft-spin 0.8s linear infinite;
}
.draft-loading-text {
  font-size: 0.9375rem;
  font-weight: 500;
  color: #654039;
  margin: 0;
}
@keyframes draft-spin {
  to {
    transform: rotate(360deg);
  }
}
</style>

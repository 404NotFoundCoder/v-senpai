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
        <div class="flex gap-3">
          <!-- 參考資料不受回饋狀態影響，回饋後仍可查看。 -->
          <button
            class="text-xs text-primary-800 bg-primary-200 hover:bg-primary-100 transition rounded-full px-3 py-1 shadow-sm"
            @click="showMetadataDialog = true"
          >
            參考資料
          </button>

          <button
            v-if="!hasFeedback"
            class="text-xs text-primary-600 bg-primary-100 hover:bg-primary-200 transition rounded-full px-3 py-1 shadow-sm"
            @click="showFeedback = !showFeedback"
          >
            {{ showFeedback ? '收合回饋' : '給予回饋' }}
          </button>
        </div>

        <!-- 展開回饋 -->
        <div v-if="showFeedback && !hasFeedback" class="mt-2 flex gap-3 animate-fade-in">
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

        <div v-if="hasFeedback" class="feedback-received" :class="feedbackReceivedClass">
          <span aria-hidden="true">✓</span>
          <span>{{ feedbackReceivedText }}</span>
        </div>
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
              <span class="reference-source-type" :class="sourceTypeClass(ref.sourceType)">
                <component
                  :is="sourceTypeIcon(ref.sourceType)"
                  v-if="sourceTypeIcon(ref.sourceType)"
                  class="reference-source-icon"
                  aria-hidden="true"
                />
                <span>{{ sourceTypeLabel(ref.sourceType) }}</span>
              </span>
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

  <!-- 回饋後續：滿意可補充原因，不滿意可選擇生成論壇草稿 -->
  <Teleport to="body">
    <Transition name="fade">
      <div v-if="showFeedbackFollowUp" class="dislike-followup-overlay">
        <div class="dislike-followup-dialog">
          <div class="dislike-followup-header" :class="feedbackToneClass">
            <p class="dislike-followup-eyebrow">{{ feedbackFollowUpEyebrow }}</p>
            <h2 class="dislike-followup-title">{{ feedbackFollowUpTitle }}</h2>
            <p class="dislike-followup-question">
              {{ feedbackFollowUpDescription }}
            </p>
          </div>

          <label class="dislike-feedback-field">
            <span>{{ feedbackNoteLabel }}<small>選填</small></span>
            <div class="feedback-quick-options" :class="feedbackToneClass">
              <button
                v-for="option in feedbackQuickOptions"
                :key="option"
                type="button"
                @click="applyFeedbackQuickOption(option)"
              >
                {{ option }}
              </button>
            </div>
            <textarea
              v-model.trim="feedbackNoteText"
              rows="4"
              maxlength="400"
              :placeholder="feedbackNotePlaceholder"
            ></textarea>
          </label>

          <div
            class="dislike-followup-actions"
            :class="{ 'dislike-followup-actions--single': pendingFeedbackType === 'like' }"
          >
            <button
              v-if="pendingFeedbackType === 'dislike'"
              type="button"
              class="btn-generate"
              @click="handleGenerateDraft"
            >
              要，幫我生成草稿
            </button>
            <button type="button" class="btn-submit-feedback" @click="handleSubmitFeedbackNote">
              {{ pendingFeedbackType === 'like' ? '送出回饋' : '只送出回饋' }}
            </button>
          </div>
          <button type="button" class="btn-skip" @click="handleSkipFeedbackNote">
            {{ pendingFeedbackType === 'like' ? '不補充了' : '先不用' }}
          </button>
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
import { updateFeedbackDetail } from '@/composables/services/chatFirestoreService'
import { DRAFT_API_URL, FORUM_ORIGIN } from '@/config/envEndpoints'
import { formatChatTimestamp } from '@/utils/dateTime'
import { buildForumUrl, goForum } from '@/utils/forumAuth'
import { getAuth } from 'firebase/auth'
import { computed, ref } from 'vue'
import MarkdownIt from 'markdown-it'
import { BookOpen, Share2 } from '@lucide/vue'

const md = new MarkdownIt({ linkify: true })

export interface ReferenceItem {
  id: string
  source: string
  content: string
  sourceType?: 'peer_sharing' | 'teaching_material' | 'mixed' | 'unknown'
}

const props = defineProps<{
  text: string
  isSelf?: boolean
  timestamp?: string
  metadata?: string
  references?: ReferenceItem[]
  docid?: string
  feedback?: string
  userText?: string
  chatHistory?: Array<{ aiText: string; userText: string; metadata: string }>
}>()

const BASE_POST_URL = `${FORUM_ORIGIN}/post`
const refLink = (id: string) => `${BASE_POST_URL}/${id}`
const sourceTypeLabel = (sourceType?: ReferenceItem['sourceType']) => {
  if (sourceType === 'peer_sharing') return '他人分享'
  if (sourceType === 'teaching_material') return '教材'
  if (sourceType === 'mixed') return '混合'
  return '未分類'
}
const sourceTypeClass = (sourceType?: ReferenceItem['sourceType']) => ({
  'reference-source-type--teaching': sourceType === 'teaching_material',
  'reference-source-type--sharing': sourceType === 'peer_sharing',
  'reference-source-type--muted':
    sourceType !== 'teaching_material' && sourceType !== 'peer_sharing',
})
const sourceTypeIcon = (sourceType?: ReferenceItem['sourceType']) => {
  if (sourceType === 'teaching_material') return BookOpen
  if (sourceType === 'peer_sharing') return Share2
  return null
}

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
    sourceType: item?.sourceType ?? 'unknown',
  }))
})

const renderedText = computed(() => md.render(props.text || ''))

const formattedTimestamp = computed(() => {
  return formatChatTimestamp(props.timestamp)
})

const { showFeedback, feedbackGiven, showMetadataDialog, toggleFeedback, giveFeedback } =
  useFeedback()
const { showToast } = useToast()
const hasFeedback = computed(
  () => feedbackGiven.value || props.feedback === 'like' || props.feedback === 'dislike',
)
type FeedbackType = 'like' | 'dislike'
const effectiveFeedbackType = computed<FeedbackType | null>(() => {
  if (props.feedback === 'like' || props.feedback === 'dislike') return props.feedback
  return null
})
const localFeedbackType = ref<FeedbackType | null>(null)
const displayedFeedbackType = computed(() => localFeedbackType.value || effectiveFeedbackType.value)
const feedbackReceivedText = computed(() =>
  displayedFeedbackType.value === 'like'
    ? '已收到你的滿意回饋，謝謝！'
    : '已收到你的不滿意回饋，謝謝你告訴我們。',
)
const feedbackReceivedClass = computed(() => ({
  'feedback-received--like': displayedFeedbackType.value === 'like',
  'feedback-received--dislike': displayedFeedbackType.value === 'dislike',
}))

const userId = getAuth().currentUser?.uid || '' // 確保已登入

const showFeedbackFollowUp = ref(false)
const isDraftLoading = ref(false)
const feedbackNoteText = ref('')
const pendingFeedbackType = ref<FeedbackType | null>(null)
const feedbackFollowUpEyebrow = computed(() =>
  pendingFeedbackType.value === 'like' ? '滿意回饋' : '不滿意回饋',
)
const feedbackFollowUpTitle = computed(() =>
  pendingFeedbackType.value === 'like' ? '想補充哪裡有幫助嗎？' : '接下來想怎麼做？',
)
const feedbackFollowUpDescription = computed(() =>
  pendingFeedbackType.value === 'like'
    ? '可以簡單告訴我們這次回答哪裡有幫助，讓我們保留好的方向。'
    : '要我們幫你生成草稿文章，前往論壇發問嗎？或是也可以只告訴我們你的想法與建議~',
)
const feedbackNoteLabel = computed(() =>
  pendingFeedbackType.value === 'like' ? '哪裡有幫助？' : '哪裡不符合期待？',
)
const feedbackNotePlaceholder = computed(() =>
  pendingFeedbackType.value === 'like'
    ? '例如：有回答到重點、資料很相關、整理得很清楚...'
    : '例如：沒有回答到重點、資料不相關、講得太籠統...',
)
const feedbackToneClass = computed(() => ({
  'feedback-tone--like': pendingFeedbackType.value === 'like',
  'feedback-tone--dislike': pendingFeedbackType.value === 'dislike',
}))
const feedbackQuickOptions = computed(() =>
  pendingFeedbackType.value === 'like'
    ? ['回答到重點', '資料很相關', '整理得很清楚', '語氣友善', '有幫助我下一步']
    : ['沒有回答到重點', '資料不相關', '講得太籠統', '引用資料不清楚', '有錯誤資訊'],
)

async function sendFeedback(type: 'like' | 'dislike') {
  if (!props.docid || !userId) return

  await giveFeedback(userId, props.docid, type, {
    userText: props.userText,
    aiText: props.text,
    metadata: props.metadata,
    chatHistory: props.chatHistory || [],
  })

  pendingFeedbackType.value = type
  localFeedbackType.value = type
  feedbackNoteText.value = ''
  showFeedbackFollowUp.value = true
}

function closeFeedbackFollowUp() {
  showFeedbackFollowUp.value = false
  feedbackNoteText.value = ''
  pendingFeedbackType.value = null
}

function applyFeedbackQuickOption(option: string) {
  const current = feedbackNoteText.value.trim()
  if (!current) {
    feedbackNoteText.value = option
    return
  }
  if (current.includes(option)) return
  feedbackNoteText.value = `${current}、${option}`
}

function handleSkipFeedbackNote() {
  closeFeedbackFollowUp()
  showToast('感謝你的回饋！')
}

async function handleGenerateDraft() {
  showFeedbackFollowUp.value = false
  isDraftLoading.value = true
  try {
    if (props.docid && userId && pendingFeedbackType.value === 'dislike') {
      await updateFeedbackDetail(userId, props.docid, 'dislike', feedbackNoteText.value)
    }
    await callDraftAPI()
    // 成功會 redirect，不需手動關閉 loading
  } catch {
    showToast('生成失敗，請稍後再試')
  } finally {
    isDraftLoading.value = false
    feedbackNoteText.value = ''
    pendingFeedbackType.value = null
  }
}

async function handleSubmitFeedbackNote() {
  const submittedType = pendingFeedbackType.value
  if (props.docid && userId && pendingFeedbackType.value) {
    await updateFeedbackDetail(
      userId,
      props.docid,
      pendingFeedbackType.value,
      feedbackNoteText.value,
    )
  }
  closeFeedbackFollowUp()
  showToast(
    submittedType === 'like'
      ? '已收到，謝謝你告訴我們哪裡有幫助'
      : '已收到，謝謝你讓我們知道問題在哪裡',
  )
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
    const response = await fetch(DRAFT_API_URL, {
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
.feedback-received {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  margin-top: 0.5rem;
  font-size: 0.8125rem;
  font-weight: 700;
}
.feedback-received--like {
  color: #2f7d50;
}
.feedback-received--dislike {
  color: #9a5f52;
}
.feedback-received span:first-child {
  display: inline-grid;
  place-items: center;
  width: 0.9rem;
  height: 0.9rem;
  border-radius: 0.2rem;
  color: #fff;
  background: #61b77a;
  font-size: 0.7rem;
  line-height: 1;
}
.feedback-received--like span:first-child {
  background: #61b77a;
}
.feedback-received--dislike span:first-child {
  background: #b8796d;
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
  flex-wrap: wrap;
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
.reference-source-type {
  display: inline-flex;
  align-items: center;
  flex: 0 0 auto;
  gap: 0.35rem;
  border-radius: 999px;
  font-size: 0.8125rem;
  font-weight: 800;
  line-height: 1;
  padding: 0.45rem 0.8rem;
}
.reference-source-icon {
  flex: 0 0 auto;
  width: 0.9rem;
  height: 0.9rem;
  stroke-width: 2.25;
}
.reference-source-type--teaching {
  border: 1px solid rgba(224, 149, 42, 0.58);
  color: #b8610e;
  background: #fffaf0;
}
.reference-source-type--sharing {
  border: 1px solid rgba(88, 176, 226, 0.5);
  color: #1677a8;
  background: #f0faff;
}
.reference-source-type--muted {
  border: 1px solid rgba(167, 111, 101, 0.24);
  color: #87564d;
  background: rgba(255, 255, 255, 0.45);
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
  background: rgba(63, 40, 37, 0.32);
  backdrop-filter: blur(6px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9998;
  padding: 1rem;
}
.dislike-followup-dialog {
  background: #fff;
  border-radius: 1.25rem;
  padding: 1.5rem;
  max-width: 27rem;
  width: 100%;
  box-shadow:
    0 24px 56px rgba(63, 40, 37, 0.18),
    0 0 0 1px rgba(201, 146, 136, 0.2);
}
.dislike-followup-header {
  margin-bottom: 1rem;
}
.dislike-followup-eyebrow {
  font-size: 0.8125rem;
  font-weight: 800;
  color: #a76f65;
  margin: 0 0 0.35rem;
}
.feedback-tone--like .dislike-followup-eyebrow {
  color: #2f8d58;
}
.feedback-tone--dislike .dislike-followup-eyebrow {
  color: #a76f65;
}
.dislike-followup-title {
  font-size: 1.25rem;
  font-weight: 900;
  color: #654039;
  line-height: 1.3;
  margin: 0;
}
.dislike-followup-question {
  font-size: 0.9375rem;
  color: #654039;
  line-height: 1.5;
  margin: 0.5rem 0 0;
}
.dislike-feedback-field {
  display: grid;
  gap: 0.5rem;
  margin-bottom: 1rem;
}
.dislike-feedback-field span {
  font-size: 0.875rem;
  font-weight: 800;
  color: #654039;
}
.dislike-feedback-field small {
  margin-left: 0.35rem;
  color: #a9847a;
  font-size: 0.75rem;
  font-weight: 700;
}
.feedback-quick-options {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
}
.feedback-quick-options button {
  border: 1px solid rgba(201, 146, 136, 0.34);
  border-radius: 999px;
  background: #fffaf5;
  color: #87564d;
  cursor: pointer;
  font-size: 0.8125rem;
  font-weight: 800;
  line-height: 1;
  padding: 0.48rem 0.7rem;
  transition:
    background 0.2s ease,
    border-color 0.2s ease,
    color 0.2s ease,
    transform 0.2s ease;
}
.feedback-quick-options button:hover {
  background: #fbecdc;
  border-color: rgba(167, 111, 101, 0.52);
  transform: translateY(-1px);
}
.feedback-quick-options.feedback-tone--like button {
  border-color: rgba(80, 172, 111, 0.32);
  background: #f1fbf5;
  color: #2f7d50;
}
.feedback-quick-options.feedback-tone--like button:hover {
  background: #e4f7ea;
  border-color: rgba(47, 141, 88, 0.46);
}
.dislike-feedback-field textarea {
  width: 100%;
  resize: vertical;
  min-height: 6rem;
  border: 1px solid rgba(201, 146, 136, 0.34);
  border-radius: 0.75rem;
  background: #fffaf5;
  color: #654039;
  font-size: 0.9375rem;
  line-height: 1.55;
  outline: none;
  padding: 0.75rem 0.85rem;
  transition:
    border-color 0.2s ease,
    box-shadow 0.2s ease,
    background 0.2s ease;
}
.dislike-feedback-field textarea::placeholder {
  color: #b19a94;
}
.dislike-feedback-field textarea:focus {
  border-color: rgba(167, 111, 101, 0.78);
  background: #fff;
  box-shadow: 0 0 0 3px rgba(167, 111, 101, 0.12);
}
.dislike-followup-actions {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: 0.75rem;
}
.dislike-followup-actions--single {
  grid-template-columns: 1fr;
}
.btn-generate {
  padding: 0.72rem 1rem;
  font-size: 0.9375rem;
  font-weight: 800;
  color: #fff;
  background: #a76f65;
  border: none;
  border-radius: 0.75rem;
  cursor: pointer;
  transition:
    background 0.2s,
    transform 0.2s,
    box-shadow 0.2s;
  box-shadow: 0 8px 18px rgba(167, 111, 101, 0.22);
}
.btn-generate:hover {
  background: #87564d;
  transform: translateY(-1px);
  box-shadow: 0 10px 22px rgba(135, 86, 77, 0.24);
}
.btn-submit-feedback {
  padding: 0.72rem 1rem;
  font-size: 0.9375rem;
  font-weight: 800;
  color: #87564d;
  background: #fff4ea;
  border: 1px solid rgba(201, 146, 136, 0.42);
  border-radius: 0.75rem;
  cursor: pointer;
  transition:
    background 0.2s,
    border-color 0.2s,
    transform 0.2s;
}
.btn-submit-feedback:hover {
  background: #fbecdc;
  border-color: rgba(167, 111, 101, 0.5);
  transform: translateY(-1px);
}
.btn-skip {
  display: block;
  margin: 0.8rem auto 0;
  padding: 0.35rem 0.5rem;
  font-size: 0.875rem;
  font-weight: 700;
  color: #9a7770;
  background: transparent;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  transition:
    color 0.2s,
    background 0.2s;
}
.btn-skip:hover {
  color: #654039;
  background: #fff4ea;
}
@media (max-width: 420px) {
  .dislike-followup-actions {
    grid-template-columns: 1fr;
  }
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

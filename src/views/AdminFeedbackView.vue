<template>
  <MainPageShell>
    <main class="admin-feedback-page">
      <header class="admin-feedback-header">
        <div>
          <p class="admin-feedback-eyebrow">Admin</p>
          <h1>聊天回饋總覽</h1>
          <p>依時間由新到舊查看使用者對 AI 回答的滿意與不滿意回饋。</p>
        </div>
        <button type="button" class="refresh-button" :disabled="loading" @click="loadFeedback">
          重新整理
        </button>
      </header>

      <section class="feedback-summary" aria-label="回饋統計">
        <button
          type="button"
          class="summary-card summary-card--dislike"
          :class="{ 'summary-card--active': activeTab === 'dislike' }"
          @click="activeTab = 'dislike'"
        >
          <span>不滿意</span>
          <strong>{{ dislikeFeedback.length }}</strong>
        </button>
        <button
          type="button"
          class="summary-card summary-card--like"
          :class="{ 'summary-card--active': activeTab === 'like' }"
          @click="activeTab = 'like'"
        >
          <span>滿意</span>
          <strong>{{ likeFeedback.length }}</strong>
        </button>
      </section>

      <section class="feedback-panel">
        <div class="feedback-panel-header">
          <h2>{{ activeTab === 'dislike' ? 'public-feedback-dislike' : 'public-feedback-like' }}</h2>
          <span>createdAt desc</span>
        </div>

        <div v-if="loading" class="empty-state">讀取中...</div>
        <div v-else-if="visibleFeedback.length === 0" class="empty-state">目前沒有回饋資料</div>

        <div v-else class="feedback-list">
          <article v-for="item in visibleFeedback" :key="item.id" class="feedback-card">
            <div class="feedback-card-top">
              <span class="feedback-id">ID: {{ item.id }}</span>
              <time>{{ formatDate(item.createdAt) }}</time>
            </div>

            <div class="feedback-meta">
              <span>{{ item.uid || '無 UID' }}</span>
              <span v-if="feedbackNoteUpdatedAt(item)">
                補充於 {{ formatDate(feedbackNoteUpdatedAt(item)) }}
              </span>
            </div>

            <div class="feedback-note">
              <p class="field-label">使用者補充</p>
              <p>{{ feedbackNote(item) || '未填寫' }}</p>
            </div>

            <div class="feedback-grid">
              <section>
                <p class="field-label">使用者問題</p>
                <p>{{ item.userText || '無內容' }}</p>
              </section>
              <section>
                <p class="field-label">AI 回答</p>
                <p>{{ item.aiText || '無內容' }}</p>
              </section>
            </div>

            <details v-if="item.metadata || item.chatHistory?.length" class="feedback-details">
              <summary>查看參考資料與前文</summary>
              <div v-if="item.metadata" class="metadata-block">{{ item.metadata }}</div>
              <ol v-if="item.chatHistory?.length" class="history-list">
                <li v-for="(history, index) in item.chatHistory" :key="index">
                  <strong>Q:</strong> {{ history.userText }}
                  <br />
                  <strong>A:</strong> {{ history.aiText }}
                </li>
              </ol>
            </details>
          </article>
        </div>
      </section>
    </main>
  </MainPageShell>
</template>

<script setup lang="ts">
import MainPageShell from '@/components/layout/MainPageShell.vue'
import { db } from '@/config/firebaseConfig'
import { collection, getDocs, orderBy, query } from 'firebase/firestore'
import { computed, onMounted, ref } from 'vue'

type FeedbackTab = 'dislike' | 'like'

interface PublicFeedback {
  id: string
  uid?: string
  userText?: string
  aiText?: string
  metadata?: string
  likeNote?: string
  dislikeNote?: string
  createdAt?: any
  likeNoteUpdatedAt?: any
  dislikeNoteUpdatedAt?: any
  chatHistory?: Array<{ aiText: string; userText: string; metadata?: string }>
}

const activeTab = ref<FeedbackTab>('dislike')
const loading = ref(true)
const dislikeFeedback = ref<PublicFeedback[]>([])
const likeFeedback = ref<PublicFeedback[]>([])

const visibleFeedback = computed(() =>
  activeTab.value === 'dislike' ? dislikeFeedback.value : likeFeedback.value,
)

function formatDate(timestamp: any): string {
  if (!timestamp) return '未知時間'
  const date = timestamp.toDate ? timestamp.toDate() : new Date(timestamp)
  return date.toLocaleString('zh-TW', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

async function loadCollection(collectionName: string): Promise<PublicFeedback[]> {
  const q = query(collection(db, collectionName), orderBy('createdAt', 'desc'))
  const snapshot = await getDocs(q)

  return snapshot.docs.map((docSnap) => {
    const data = docSnap.data()
    return {
      id: docSnap.id,
      uid: data.uid || '',
      userText: data.userText || '',
      aiText: data.aiText || '',
      metadata: data.metadata || '',
      likeNote: data.likeNote || '',
      dislikeNote: data.dislikeNote || '',
      createdAt: data.createdAt,
      likeNoteUpdatedAt: data.likeNoteUpdatedAt,
      dislikeNoteUpdatedAt: data.dislikeNoteUpdatedAt,
      chatHistory: Array.isArray(data.chatHistory) ? data.chatHistory : [],
    }
  })
}

function feedbackNote(item: PublicFeedback): string {
  return activeTab.value === 'like' ? item.likeNote || '' : item.dislikeNote || ''
}

function feedbackNoteUpdatedAt(item: PublicFeedback): any {
  return activeTab.value === 'like' ? item.likeNoteUpdatedAt : item.dislikeNoteUpdatedAt
}

async function loadFeedback() {
  loading.value = true
  try {
    const [dislike, like] = await Promise.all([
      loadCollection('public-feedback-dislike'),
      loadCollection('public-feedback-like'),
    ])
    dislikeFeedback.value = dislike
    likeFeedback.value = like
  } finally {
    loading.value = false
  }
}

onMounted(loadFeedback)
</script>

<style scoped>
.admin-feedback-page {
  max-width: 72rem;
  margin: 0 auto;
  padding: 6rem 1rem 3rem;
}
.admin-feedback-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.25rem;
}
.admin-feedback-eyebrow {
  margin: 0 0 0.3rem;
  color: #a76f65;
  font-size: 0.8rem;
  font-weight: 900;
}
.admin-feedback-header h1 {
  margin: 0;
  color: #654039;
  font-size: 1.8rem;
  font-weight: 900;
}
.admin-feedback-header p {
  margin: 0.45rem 0 0;
  color: #80625c;
}
.refresh-button {
  border: 1px solid rgba(167, 111, 101, 0.28);
  border-radius: 0.75rem;
  background: #fffaf5;
  color: #87564d;
  cursor: pointer;
  font-weight: 800;
  padding: 0.65rem 1rem;
}
.feedback-summary {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.85rem;
  margin-bottom: 1rem;
}
.summary-card {
  border: 1px solid rgba(201, 146, 136, 0.24);
  border-radius: 0.85rem;
  background: #fff;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  padding: 1rem;
  text-align: left;
}
.summary-card span {
  color: #80625c;
  font-weight: 800;
}
.summary-card strong {
  color: #654039;
  font-size: 1.5rem;
}
.summary-card--active {
  box-shadow: 0 0 0 3px rgba(167, 111, 101, 0.12);
}
.summary-card--dislike.summary-card--active {
  border-color: rgba(190, 93, 73, 0.45);
}
.summary-card--like.summary-card--active {
  border-color: rgba(73, 157, 105, 0.45);
}
.feedback-panel {
  background: #fff;
  border: 1px solid rgba(201, 146, 136, 0.22);
  border-radius: 1rem;
  padding: 1rem;
}
.feedback-panel-header {
  align-items: center;
  border-bottom: 1px solid rgba(201, 146, 136, 0.2);
  display: flex;
  justify-content: space-between;
  margin-bottom: 1rem;
  padding-bottom: 0.8rem;
}
.feedback-panel-header h2 {
  color: #654039;
  font-size: 1rem;
  font-weight: 900;
  margin: 0;
}
.feedback-panel-header span,
.feedback-id,
.feedback-card-top time,
.feedback-meta {
  color: #9a817b;
  font-size: 0.8rem;
}
.empty-state {
  color: #9a817b;
  padding: 2.5rem 1rem;
  text-align: center;
}
.feedback-list {
  display: grid;
  gap: 1rem;
}
.feedback-card {
  border: 1px solid rgba(201, 146, 136, 0.22);
  border-radius: 0.85rem;
  padding: 1rem;
}
.feedback-card-top,
.feedback-meta {
  display: flex;
  gap: 0.75rem;
  justify-content: space-between;
}
.feedback-meta {
  margin: 0.5rem 0 0.85rem;
}
.feedback-grid {
  display: grid;
  gap: 0.8rem;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}
.feedback-grid section,
.feedback-note {
  background: #fffaf5;
  border-radius: 0.75rem;
  color: #654039;
  line-height: 1.6;
  padding: 0.85rem;
  white-space: pre-wrap;
}
.feedback-note {
  background: #fff4ea;
  margin-bottom: 0.8rem;
}
.field-label {
  color: #a76f65;
  font-size: 0.78rem;
  font-weight: 900;
  margin: 0 0 0.35rem;
}
.feedback-details {
  margin-top: 0.8rem;
}
.feedback-details summary {
  color: #87564d;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 800;
}
.metadata-block,
.history-list {
  background: #f8f1ec;
  border-radius: 0.7rem;
  color: #654039;
  font-size: 0.85rem;
  line-height: 1.55;
  margin-top: 0.7rem;
  padding: 0.85rem;
  white-space: pre-wrap;
}
.history-list {
  padding-left: 2rem;
}
@media (max-width: 720px) {
  .admin-feedback-header,
  .feedback-card-top,
  .feedback-meta {
    align-items: flex-start;
    flex-direction: column;
  }
  .feedback-grid,
  .feedback-summary {
    grid-template-columns: 1fr;
  }
}
</style>

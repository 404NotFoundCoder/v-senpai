<template>
  <div class="max-w-5xl mx-auto mt-[60px] py-10 sm:py-20 px-6">
    <h1 class="text-2xl font-bold mb-6">👎 Dislike 反饋紀錄</h1>

    <div class="mb-6 flex justify-between items-center">
      <p class="text-gray-500">總計：{{ feedbackList.length }} 條紀錄</p>
      <button
        @click="exportToExcel"
        class="bg-green-500 hover:bg-green-600 text-white px-6 py-2 rounded shadow transition"
        :disabled="feedbackList.length === 0"
      >
        匯出 Excel
      </button>
    </div>

    <div v-if="loading" class="text-center text-gray-500">載入中...</div>

    <div v-else-if="feedbackList.length === 0" class="text-center text-gray-400 py-10">
      尚無 Dislike 反饋紀錄
    </div>

    <div v-else class="space-y-6">
      <div
        v-for="(feedback, index) in feedbackList"
        :key="feedback.id"
        class="bg-white border rounded-lg p-5 shadow-sm hover:shadow-md transition"
      >
        <div class="flex justify-between items-start mb-3">
          <span class="text-xs text-gray-400">ID: {{ feedback.id }}</span>
          <span class="text-xs text-gray-400">
            {{ formatDate(feedback.createdAt) }}
          </span>
        </div>

        <div class="mb-3">
          <p class="text-xs text-gray-500 mb-1">用户 UID:</p>
          <p class="text-sm text-gray-700 font-mono">{{ feedback.uid }}</p>
        </div>

        <div class="mb-3 bg-blue-50 p-3 rounded">
          <p class="text-xs text-blue-600 mb-1 font-semibold">👤 使用者問題:</p>
          <p class="text-sm text-gray-800">{{ feedback.userText }}</p>
        </div>

        <div class="mb-3 bg-purple-50 p-3 rounded">
          <p class="text-xs text-purple-600 mb-1 font-semibold">🤖 AI 回覆:</p>
          <p class="text-sm text-gray-800">{{ feedback.aiText }}</p>
        </div>

        <div v-if="feedback.metadata" class="bg-gray-50 p-3 rounded">
          <button
            @click="toggleMetadata(index)"
            class="text-xs text-indigo-600 hover:underline focus:outline-none mb-2"
          >
            {{ expandedMetadata[index] ? '🔽 收合資料來源摘要' : '▶️ 查看資料來源摘要' }}
          </button>

          <div
            v-if="expandedMetadata[index]"
            class="text-xs text-gray-600 whitespace-pre-wrap bg-white border rounded p-3"
          >
            {{ feedback.metadata }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { collection, getDocs, query, orderBy } from 'firebase/firestore'
import { db } from '@/config/firebaseConfig'
import * as XLSX from 'xlsx'
import { saveAs } from 'file-saver'

interface DislikeFeedback {
  id: string
  uid: string
  userText: string
  aiText: string
  metadata: string
  createdAt: any
}

const feedbackList = ref<DislikeFeedback[]>([])
const expandedMetadata = ref<boolean[]>([])
const loading = ref(true)

// 切换元数据显示
function toggleMetadata(index: number) {
  expandedMetadata.value[index] = !expandedMetadata.value[index]
}

// 格式化日期
function formatDate(timestamp: any): string {
  if (!timestamp) return '未知時間'
  try {
    const date = timestamp.toDate ? timestamp.toDate() : new Date(timestamp)
    return date.toLocaleString('zh-TW', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch {
    return '未知時間'
  }
}

// 从 Firestore 加载数据
async function loadDislikeFeedback() {
  loading.value = true
  try {
    const q = query(collection(db, 'public-feedback-dislike'), orderBy('createdAt', 'desc'))
    const snapshot = await getDocs(q)

    feedbackList.value = snapshot.docs.map((doc) => ({
      id: doc.id,
      uid: doc.data().uid || '',
      userText: doc.data().userText || '',
      aiText: doc.data().aiText || '',
      metadata: doc.data().metadata || '',
      createdAt: doc.data().createdAt,
    }))

    expandedMetadata.value = Array(feedbackList.value.length).fill(false)
    console.log('✅ 加載了', feedbackList.value.length, '條 dislike 反饋')
  } catch (error) {
    console.error('❌ 加載 dislike 反饋失敗:', error)
  } finally {
    loading.value = false
  }
}

// 导出到 Excel
function exportToExcel() {
  if (feedbackList.value.length === 0) {
    alert('沒有數據可導出')
    return
  }

  const exportData = feedbackList.value.map((feedback) => ({
    UID: feedback.uid,
    使用者問題: feedback.userText,
    AI回覆: feedback.aiText,
    資料來源摘要: feedback.metadata,
    反馈时间: formatDate(feedback.createdAt),
    'Message ID': feedback.id,
  }))

  const worksheet = XLSX.utils.json_to_sheet(exportData)
  const workbook = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(workbook, worksheet, 'Dislike反饋')

  // 设置列寬
  worksheet['!cols'] = [
    { wch: 30 }, // UID
    { wch: 50 }, // 使用者問題
    { wch: 50 }, // AI回覆
    { wch: 60 }, // 資料來源摘要
    { wch: 20 }, // 反饋時間
    { wch: 30 }, // Message ID
  ]

  const wbout = XLSX.write(workbook, { bookType: 'xlsx', type: 'array' })
  const blob = new Blob([wbout], { type: 'application/octet-stream' })

  const now = new Date().toISOString().slice(0, 10)
  saveAs(blob, `dislike-feedback-${now}.xlsx`)
}

onMounted(() => {
  loadDislikeFeedback()
})
</script>

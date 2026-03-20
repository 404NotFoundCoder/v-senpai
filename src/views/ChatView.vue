<template>
  <div class="flex flex-col h-screen">
    <!-- 中間聊天訊息區 -->
    <div class="flex-1 overflow-y-auto">
      <ChatBox :messages="messages" :is-thinking="isThinking" />
    </div>
    <div class="suggested-slot">
      <SuggestedQuestions
        :questions="[
          '從系統分析與設計課程中遇到什麼問題？如何解決？',
          '使用 git 嗎？',
          '使用哪個語言、資料庫開發？為什麼選擇它？優缺點是？',
          '使用生成式人工智慧嗎？如何使用？遇到什麼問題？',
          '如何定期追蹤組員進度？遇到什麼問題？',
          '對各位的建議是？',
        ]"
        @select="handleSuggestedQuestion"
      />
    </div>
    <!-- 輸入框區：Shift+Enter 換行、Enter 發送，RWD 響應式 -->
    <div class="chat-input-area">
      <div class="chat-input-wrap">
        <textarea
          ref="inputRef"
          v-model="input"
          placeholder="輸入訊息...（Shift+Enter 換行，Enter 發送）"
          rows="1"
          class="chat-input"
          @keydown="handleKeydown"
          @input="autoResize"
        />
        <button type="button" class="chat-send-btn" :disabled="!input.trim()" @click="sendMessage">
          發送
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, watch } from 'vue'
import ChatBox from '../components/chat/ChatBox.vue'
import { useChatService } from '@/composables/useChatService'
import { watchFirestoreMessages } from '@/composables/services/chatFirestoreService'
import { onAuthStateChanged } from 'firebase/auth'
import { auth } from '@/config/firebaseConfig'
import SuggestedQuestions from '../components/chat/SuggestedQuestions.vue'

// 狀態
const input = ref('')
const inputRef = ref<HTMLTextAreaElement | null>(null)
const isThinking = ref(false)
const messages = ref([])

const MIN_ROWS = 1
const MAX_ROWS = 6
const LINE_HEIGHT = 24

function autoResize() {
  nextTick(() => {
    const el = inputRef.value
    if (!el) return
    if (!el.value.trim()) {
      el.style.height = `${MIN_ROWS * LINE_HEIGHT}px`
      return
    }
    el.style.height = 'auto'
    const minH = MIN_ROWS * LINE_HEIGHT
    const maxH = MAX_ROWS * LINE_HEIGHT
    el.style.height = `${Math.min(maxH, Math.max(minH, el.scrollHeight))}px`
  })
}

// 傳送後 input 被清空時，程式不會觸發 @input，需用 watch 強制重置為單行高度
watch(input, (val) => {
  if (!val.trim()) nextTick(() => autoResize())
})

function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    sendMessage()
  }
}

// 注入主邏輯
const { sendMessage, readUserData, handleSuggestedQuestion } = useChatService(
  messages,
  input,
  isThinking,
)

// 預設訊息
const defaultMessage = {
  sender: 'ai',
  text:
    '👋 嗨～我是你的學長姊模擬助理 V-Senpai！\n' +
    '我整理了歷屆學長姊在「系統分析與設計」課程中的經驗與建議，\n' +
    '不管是選題、合作、技術、還是報告準備，你都可以問我唷～\n' +
    '如果不知道從哪裡開始，也可以點選下方的引導問題來試試看 👇',
  createdAt: new Date().toISOString(),
  metadata: '這是開場訊息',
  docid: 'init-msg',
}

// 初始化
onAuthStateChanged(auth, (user) => {
  if (user) {
    // console.log('✅ 已登入:', user.uid)
    readUserData(user.uid)
    watchFirestoreMessages(user.uid, messages, defaultMessage)
  } else {
    console.warn('⚠️ 尚未登入，sendMessage 不會作用')
  }
})
</script>

<style scoped>
.suggested-slot {
  position: relative;
  height: 0;
  overflow: visible;
}

.chat-input-area {
  background: #fff;
  padding: 0.75rem 1rem;
  padding-bottom: max(0.75rem, env(safe-area-inset-bottom));
  box-shadow: 0 -1px 3px rgba(0, 0, 0, 0.06);
}
.chat-input-wrap {
  display: flex;
  align-items: flex-end;
  gap: 0.5rem;
  max-width: 56rem;
  margin: 0 auto;
  width: 100%;
}
.chat-input {
  flex: 1;
  min-width: 0;
  min-height: 2.5rem;
  max-height: 9rem;
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  font-size: 1rem;
  line-height: 1.5;
  resize: none;
  overflow-y: auto;
  transition:
    border-color 0.2s,
    box-shadow 0.2s;
}
.chat-input:focus {
  outline: none;
  border-color: #e4b2a0;
  box-shadow: 0 0 0 2px rgba(228, 178, 160, 0.3);
}
.chat-input::placeholder {
  color: #9ca3af;
}
.chat-send-btn {
  flex-shrink: 0;
  min-height: 2.5rem;
  padding: 0.5rem 1rem;
  font-weight: 600;
  font-size: 0.9375rem;
  color: #fff;
  background: #c79288;
  border: none;
  border-radius: 0.5rem;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  cursor: pointer;
  transition:
    background 0.2s,
    box-shadow 0.2s;
}
.chat-send-btn:hover:not(:disabled) {
  background: #a76f65;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
.chat-send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* RWD：平板 */
@media (min-width: 640px) {
  .chat-input-area {
    padding: 1rem 1.5rem;
  }
  .chat-input-wrap {
    gap: 0.75rem;
  }
  .chat-input {
    padding: 0.625rem 1rem;
  }
  .chat-send-btn {
    min-height: 2.75rem;
    padding: 0.5rem 1.25rem;
    font-size: 1rem;
  }
}

/* RWD：桌面 */
@media (min-width: 1024px) {
  .chat-input-area {
    padding: 0.75rem 1.5rem 1rem;
  }
}

/* RWD：手機觸控優化（最小觸控面積 44px） */
@media (max-width: 639px) {
  .chat-send-btn {
    min-height: 2.75rem;
    min-width: 2.75rem;
  }
}
</style>

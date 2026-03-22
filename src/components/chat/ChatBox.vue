<template>
  <!-- 不在此層 overflow：捲動只發生在 ChatView .chat-scroll，避免 iOS 雙層捲動失效 -->
  <div class="mt-16 space-y-2 bg-gray-50 px-4 py-3 pb-8 sm:mt-20 sm:px-6 lg:px-10">
    <ChatBubble
      v-for="(msg, index) in messages"
      :key="index"
      :text="msg.text || '[沒有文字]'"
      :isSelf="msg.sender === 'user'"
      :timestamp="msg.createdAt"
      :metadata="msg.metadata"
      :references="msg.references"
      :docid="msg.docid"
    />
    <!-- 等待回覆時的動態指示 -->
    <div v-if="isThinking" class="flex justify-start my-5">
      <div class="typing-indicator">
        <span class="typing-dot"></span>
        <span class="typing-dot"></span>
        <span class="typing-dot"></span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import ChatBubble from '@/components/chat/ChatBubble.vue'

defineProps<{
  messages: {
    sender: string
    text: string
    createdAt: string
    metadata?: string
    references?: { id: string; source: string; content: string }[]
    docid?: string
    feedback?: string
  }[]
  isThinking?: boolean
}>()
</script>

<style scoped>
.typing-indicator {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  padding: 1rem 1.25rem;
  background: #FBECDC;
  color: #654039;
  border-radius: 1rem 1rem 1rem 0.25rem;
  box-shadow: 0 2px 8px rgba(101, 64, 57, 0.08);
}
.typing-dot {
  width: 0.5rem;
  height: 0.5rem;
  background: #A76F65;
  border-radius: 50%;
  animation: typing-bounce 1.4s ease-in-out infinite;
}
.typing-dot:nth-child(1) { animation-delay: 0s; }
.typing-dot:nth-child(2) { animation-delay: 0.2s; }
.typing-dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes typing-bounce {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.6; }
  30% { transform: translateY(-0.35rem); opacity: 1; }
}
</style>

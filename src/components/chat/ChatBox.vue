<template>
  <div ref="chatContainer" class="mt-20 px-10 space-y-2 overflow-y-auto bg-gray-50 h-full">
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
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import ChatBubble from '@/components/chat/ChatBubble.vue'

const props = defineProps<{
  messages: {
    sender: string
    text: string
    createdAt: string
    metadata?: string
    references?: { id: string; source: string; content: string }[]
    docid?: string
    feedback?: string
  }[]
}>()

const chatContainer = ref<HTMLElement | null>(null)
const previousHeight = ref(0)

watch(
  () => props.messages.length,
  async () => {
    const el = chatContainer.value
    if (!el) return

    // 儲存原本的滾動高度
    previousHeight.value = el.scrollHeight

    await nextTick()

    const newHeight = el.scrollHeight
    const heightDiff = newHeight - previousHeight.value

    // 自然往下滾一格
    el.scrollTop += heightDiff
  },
)
</script>

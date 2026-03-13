<template>
  <div ref="chatContainer" class="mt-16 sm:mt-20 px-4 sm:px-6 lg:px-10 py-3 space-y-2 overflow-y-auto bg-gray-50 h-full">
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

watch(
  () => props.messages,
  async () => {
    await nextTick()
    const el = chatContainer.value
    if (!el) return
    el.scrollTop = el.scrollHeight
  },
  { deep: true },
)
</script>

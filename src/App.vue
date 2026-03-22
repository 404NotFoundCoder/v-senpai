<script setup lang="ts">
import { computed } from 'vue'
import { RouterView, useRoute } from 'vue-router'
import Header from './components/Header.vue'
import Footer from './components/Footer.vue'
import ToastBar from './components/ui/ToastBar.vue'

const route = useRoute()
/** 聊天室：只在中間層捲動；其他頁：長內容捲中間區，footer 固定在視窗底部不浮起 */
const isChat = computed(() => route.name === 'chat')
</script>

<template>
  <div class="flex h-full min-h-0 flex-1 flex-col">
    <ToastBar />
    <Header />
    <div
      class="flex min-h-0 min-w-0 flex-1 flex-col"
      :class="isChat ? 'overflow-hidden' : 'overflow-y-auto'"
    >
      <RouterView />
    </div>
    <Footer class="shrink-0" />
  </div>
</template>

<style scoped></style>

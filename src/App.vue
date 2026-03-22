<script setup lang="ts">
import { RouterView } from 'vue-router'
import Header from './components/Header.vue'
import Footer from './components/Footer.vue'
import ToastBar from './components/ui/ToastBar.vue'
</script>

<template>
  <!-- 中間層一律 overflow-hidden（與聊天室相同），捲動交給各頁 MainPageShell / ChatView -->
  <div class="flex h-full min-h-0 flex-1 flex-col">
    <ToastBar />
    <Header />
    <div class="flex min-h-0 min-w-0 flex-1 flex-col overflow-hidden">
      <RouterView />
    </div>
    <Footer class="shrink-0" />
  </div>
</template>

<style scoped></style>

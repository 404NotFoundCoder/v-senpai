<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
import Header from './components/Header.vue'
import Footer from './components/Footer.vue'
import HelloWorld from './components/HelloWorld.vue'
import ToastBar from './components/ui/ToastBar.vue'
</script>

<template>
  <!-- flex-1+min-h-0+h-full：吃滿 #app；中間區 overflow-hidden 收斂高度，避免聊天頁整頁被撐高 -->
  <div class="flex h-full min-h-0 flex-1 flex-col">
    <ToastBar />
    <Header />
    <div class="flex min-h-0 min-w-0 flex-1 flex-col">
      <RouterView />
    </div>
    <Footer />
  </div>
</template>

<style scoped></style>

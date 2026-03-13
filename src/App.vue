<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
import Header from './components/Header.vue'
import Footer from './components/Footer.vue'
import HelloWorld from './components/HelloWorld.vue'
import ToastBar from './components/ui/ToastBar.vue'
</script>

<template>
  <div class="min-h-screen flex flex-col">
    <ToastBar />
    <Header />
    <div class="flex flex-col flex-1">
      <RouterView />
    </div>
    <Footer />
  </div>
</template>

<style scoped></style>

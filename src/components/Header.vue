<template>
  <header class="bg-primary-100 shadow-md fixed top-0 left-0 w-full z-50">
    <div
      class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-14 flex items-center justify-between w-full"
    >
      <!-- 左邊：Logo -->
      <router-link to="/" class="">
        <img src="/logo.png" alt="V-Senpai Logo" class="h-[50px] object-contain" />
      </router-link>

      <!-- 桌面版導覽列 -->
      <nav class="hidden md:flex space-x-6 items-center">
        <router-link v-if="user" to="/chat" class="text-gray-700 hover:text-primary-600"
          >聊天室</router-link
        >
        <!-- <router-link v-if="user" to="/personal" class="text-gray-700 hover:text-primary-600"
          >個人設置</router-link
        > -->
        <router-link v-if="user" to="/feedback" class="text-gray-700 hover:text-primary-600"
          >意見回饋</router-link
        >
        <!-- 登入按鈕 -->
        <button
          class="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition"
          @click="handleAuth"
        >
          {{ user ? '登出' : 'GitHub 登入' }}
        </button>
      </nav>

      <!-- 手機版：漢堡選單 -->
      <button class="md:hidden text-gray-600" @click="toggleMenu">
        <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M4 6h16M4 12h16M4 18h16"
          />
        </svg>
      </button>
    </div>

    <!-- 手機版下拉選單 -->
    <transition name="slide-fade">
      <nav v-if="isOpen" class="flex flex-col md:hidden px-4 pt-2 pb-4 bg-white shadow-md border-t">
        <router-link v-if="user" to="/chat" class="py-2 text-gray-700 hover:text-primary-600"
          >聊天室</router-link
        >
        <router-link v-if="user" to="/personal" class="py-2 text-gray-700 hover:text-primary-600"
          >個人設置</router-link
        >
        <router-link v-if="user" to="/feedback" class="py-2 text-gray-700 hover:text-primary-600"
          >意見回饋</router-link
        >
        <button
          class="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition"
          @click="handleAuth"
        >
          {{ user ? '登出' : 'GitHub 登入' }}
        </button>
      </nav>
    </transition>
  </header>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useAuth } from '@/composables/useAuth'
import { useRouter } from 'vue-router'
import { getAuth, onAuthStateChanged } from 'firebase/auth'

const isOpen = ref(false)
const toggleMenu = () => {
  isOpen.value = !isOpen.value
}
const auth = getAuth()
const router = useRouter()
const { user, signInWithGitHub, logout } = useAuth()

function handleAuth() {
  if (user.value) {
    logout()
    console.log('登出')
  } else {
    signInWithGitHub()
    console.log('GitHub 登入')
  }
}

onMounted(() => {
  // 這裡可以添加任何需要在組件掛載後執行的邏輯

  onAuthStateChanged(auth, (user) => {
    if (user) {
      console.log('User is signed in:', user)
    } else {
      console.log('No user is signed in.')
    }
  })
})
</script>

<style scoped>
.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: all 0.3s ease;
}
.slide-fade-enter-from {
  opacity: 0;
  transform: translateY(-10px);
}
.slide-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>

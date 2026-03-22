<template>
  <header class="bg-primary-100 shadow-md fixed top-0 left-0 w-full z-50">
    <div
      class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-14 flex items-center justify-between w-full"
    >
      <!-- 左邊：Logo -->
      <router-link to="/" class="" @click="closeMenu">
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
        <button
          v-if="user"
          type="button"
          class="text-gray-700 hover:text-primary-600"
          @click="openForum"
        >
          論壇
        </button>
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

    <!-- 遮罩 + 選單同一層、關閉時 leave:0 立即移除，避免白底漸隱露出粉橘底造成閃爍 -->
    <transition name="mobile-menu" :duration="{ enter: 200, leave: 0 }">
      <div v-if="isOpen" class="md:hidden mobile-menu-root">
        <button
          type="button"
          class="mobile-nav-backdrop"
          aria-label="關閉選單"
          @click="closeMenu"
        />
        <nav class="mobile-nav-panel flex flex-col px-4 pt-2 pb-4 bg-white shadow-md border-t">
          <router-link
            v-if="user"
            to="/chat"
            class="py-2 text-gray-700 hover:text-primary-600"
            @click="closeMenu"
            >聊天室</router-link
          >
          <!-- <router-link v-if="user" to="/personal" class="py-2 text-gray-700 hover:text-primary-600"
          >個人設置</router-link
        > -->
          <router-link
            v-if="user"
            to="/feedback"
            class="py-2 text-gray-700 hover:text-primary-600"
            @click="closeMenu"
            >意見回饋</router-link
          >
          <button
            v-if="user"
            type="button"
            class="py-2 text-gray-700 hover:text-primary-600 text-left"
            @click="onForumClick"
          >
            論壇
          </button>
          <button
            class="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition"
            @click="onAuthClick"
          >
            {{ user ? '登出' : 'GitHub 登入' }}
          </button>
        </nav>
      </div>
    </transition>
  </header>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch } from 'vue'
import { useAuth } from '@/composables/useAuth'
import { useToast } from '@/composables/useToast'
import { useRoute } from 'vue-router'
import { getAuth, onAuthStateChanged } from 'firebase/auth'
import { goForum } from '@/utils/forumAuth'

/** 手機選單預設關閉（勿改為 true，避免一進頁就展開） */
const isOpen = ref(false)

function closeMenu() {
  isOpen.value = false
}

function toggleMenu() {
  isOpen.value = !isOpen.value
}

function onEscape(e: KeyboardEvent) {
  if (e.key === 'Escape') closeMenu()
}

function closeMenuIfDesktop() {
  if (typeof window !== 'undefined' && window.matchMedia('(min-width: 768px)').matches) {
    closeMenu()
  }
}

const route = useRoute()
watch(
  () => route.fullPath,
  () => {
    closeMenu()
  },
)
const auth = getAuth()
const { user, signInWithGitHub, logout } = useAuth()
const { showToast } = useToast()

function handleAuth() {
  if (user.value) {
    logout()
    console.log('登出')
  } else {
    signInWithGitHub()
    console.log('GitHub 登入')
  }
}

function onAuthClick() {
  closeMenu()
  handleAuth()
}

async function openForum() {
  try {
    await goForum('/')
  } catch (error) {
    console.error('論壇跳轉失敗:', error)
    showToast('論壇登入連結建立失敗，請稍後再試', 'info')
  }
}

async function onForumClick() {
  closeMenu()
  await openForum()
}

onMounted(() => {
  // 防呆：避免 HMR／異常狀態讓選單以展開狀態進頁
  isOpen.value = false
  window.addEventListener('keydown', onEscape)
  window.addEventListener('resize', closeMenuIfDesktop)

  onAuthStateChanged(auth, (user) => {
    if (user) {
      console.log('User is signed in:', user)
    } else {
      console.log('No user is signed in.')
    }
  })
})

onUnmounted(() => {
  window.removeEventListener('keydown', onEscape)
  window.removeEventListener('resize', closeMenuIfDesktop)
})
</script>

<style scoped>
/* 手機選單遮罩：頂欄 h-14 = 3.5rem 以下不遮，點其餘畫面關閉 */
.mobile-nav-backdrop {
  position: fixed;
  inset: 3.5rem 0 0 0;
  z-index: 40;
  border: none;
  padding: 0;
  margin: 0;
  width: 100%;
  cursor: default;
  background: rgba(0, 0, 0, 0.35);
}

.mobile-nav-panel {
  position: relative;
  z-index: 50;
}

/* 僅「開啟」淡入；關閉 leave duration=0，不跑 CSS transition，避免粉橘底閃一下 */
.mobile-menu-enter-active {
  transition: opacity 0.2s ease-out;
}
.mobile-menu-enter-active .mobile-nav-panel {
  transition: transform 0.2s ease-out;
}
.mobile-menu-enter-from {
  opacity: 0;
}
.mobile-menu-enter-from .mobile-nav-panel {
  transform: translateY(-6px);
}
.mobile-menu-enter-to .mobile-nav-panel {
  transform: translateY(0);
}

.mobile-menu-leave-active {
  transition: none !important;
}
</style>

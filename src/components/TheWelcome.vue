<template>
  <!-- 勿用 min-h-screen：會多撐 100vh 導致整頁可捲、footer 像浮起。改填滿主內容區並置中 -->
  <div
    class="flex min-h-0 flex-1 flex-col items-center justify-center bg-gradient-to-br from-[#fdfefe] to-[#f5f7fa] px-4 py-10 text-gray-800 sm:px-6"
  >
    <div class="text-center w-full max-w-xl p-10">
      <h1 class="text-3xl sm:text-4xl font-extrabold mb-4 leading-snug">
        歡迎來到 <span class="text-primary-500 animate-pulse">V-Senpai</span> 🎓
      </h1>

      <p class="text-base sm:text-lg text-gray-600 mb-4">
        我是你的學長姐小助手，幫你解答系統分析與專題相關的疑惑
      </p>

      <p class="text-sm sm:text-base text-gray-700 mb-3 leading-relaxed">
        請先登入 GitHub，並在授權畫面確認授權給
        <span class="font-semibold text-indigo-500">GuaYourGuava1919 and 404NotFoundCoder</span>。
      </p>

      <p class="text-xs sm:text-sm text-gray-500 italic mb-6">📝 阿緹 & 書妤的論文需要你❤️</p>

      <ImageCarousel class="mb-6" />
    </div>
  </div>
</template>

<script setup>
import ImageCarousel from '@/components/ImageCarousel.vue'

// 範例點擊用：可改為打開文件連結
function goToDocs() {
  window.open('https://your-doc-link.example.com', '_blank')
}
</script>

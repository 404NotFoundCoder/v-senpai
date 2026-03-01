<template>
  <div class="">
    <footer class="bg-primary-100 border-t py-4 w-full text-center text-sm text-gray-600">
      <div class="max-w-5xl mx-auto px-4 text-center space-y-2">
        <p class="text-sm text-gray-600">
          &copy; 2026 GuaYourGuava & 404NotFoundCoder. All rights reserved.
        </p>
        <nav class="flex flex-wrap justify-center gap-4 text-sm">
          <a
            href="#"
            class="text-gray-700 hover:text-primary-500 hover:underline"
            @click.prevent="openPolicy"
          >
            隱私權政策
          </a>
          <a
            href="#"
            class="text-gray-700 hover:text-primary-500 hover:underline"
            @click.prevent="openTerms"
          >
            使用條款
          </a>
          <a
            href="https://mail.google.com/mail/?view=cm&fs=1&to=konigiwa00@gmail.com"
            target="_blank"
            class="text-gray-700 hover:text-primary-500 hover:underline"
          >
            聯絡阿緹與書妤
          </a>
        </nav>
      </div>
    </footer>

    <!-- Modal -->
    <div
      v-if="showTerms || showPolicy"
      class="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50 p-5"
    >
      <div
        class="bg-white w-full h-[90vh] max-w-3xl sm:rounded-2xl shadow-2xl overflow-hidden flex flex-col animate-popup"
      >
        <!-- Sticky Header -->
        <div
          class="sticky top-0 z-10 bg-white px-4 sm:px-8 pt-4 pb-2 border-b flex justify-between items-center"
        >
          <h2 class="text-lg font-semibold text-primary-800">
            📜 {{ showTerms ? '使用條款' : '隱私權政策' }}
          </h2>
          <button
            class="p-2 text-2xl font-bold text-gray-400 hover:text-green-500 transition"
            @click="closeModal"
            aria-label="關閉"
          >
            &times;
          </button>
        </div>

        <!-- 條款內容 -->
        <div
          class="flex-1 overflow-y-auto px-4 sm:px-8 py-4 prose prose-sm sm:prose-base max-w-none text-gray-700 leading-relaxed"
          v-html="showTerms ? termsHtml : policyHtml"
        />

        <!-- Sticky Footer 按鈕 -->
        <div class="sticky bottom-0 z-10 bg-white px-4 sm:px-8 pb-6 pt-4 border-t">
          <button
            class="w-full bg-green-500 hover:bg-green-600 text-white font-medium py-3 text-base sm:text-lg rounded-lg shadow transition"
            @click="closeModal"
          >
            ✅ 我已閱讀並同意(使用本系統視同同意條款)
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { marked } from 'marked'

const termsHtml = ref('')
const policyHtml = ref('')
const showTerms = ref(false)
const showPolicy = ref(false)

function openTerms() {
  fetch('/terms.md')
    .then((res) => res.text())
    .then((text) => {
      termsHtml.value = marked(text)
      showTerms.value = true
      showPolicy.value = false
    })
}

function openPolicy() {
  fetch('/privacy-policy.md')
    .then((res) => res.text())
    .then((text) => {
      policyHtml.value = marked(text)
      showPolicy.value = true
      showTerms.value = false
    })
}

function closeModal() {
  showTerms.value = false
  showPolicy.value = false
}
</script>

<style scoped>
@keyframes fade-in {
  from {
    opacity: 0;
    transform: scale(0.96);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.animate-fade-in {
  animation: fade-in 0.3s ease-out;
}
</style>

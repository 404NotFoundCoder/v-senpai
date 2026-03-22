<template>
  <MainPageShell>
    <div
      class="mx-auto max-w-3xl bg-white px-8 pb-12 pt-16 text-gray-800 sm:max-w-4xl sm:py-10"
    >
      <h1 class="mb-6 text-center text-3xl font-bold">📝 V-Senpai 使用回饋調查</h1>
      <p class="mb-6 text-center leading-relaxed">
        感謝你使用 V-Senpai！我們希望透過這份問卷了解你的使用體驗，並持續改進我們的服務。
      </p>

      <FeedbackForm
        v-model:errorFeedback="errorFeedback"
        v-model:favoritePart="favoritePart"
        v-model:suggestion="suggestion"
        v-model:screenshotBase64="screenshotBase64"
      />

      <div class="mt-6 flex justify-center">
        <button
          class="rounded-lg bg-blue-600 px-6 py-2 text-white transition hover:bg-blue-700"
          @click="handleSubmit"
        >
          提交回饋
        </button>
      </div>

      <p v-if="submitted" class="mt-4 text-center font-medium text-green-600">
        💖 感謝你的寶貴意見，我們會持續改進！
      </p>
    </div>
  </MainPageShell>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import type { User } from 'firebase/auth'
import { db, auth } from '@/config/firebaseConfig'
import { onAuthStateChanged } from 'firebase/auth'
import { collection, addDoc, serverTimestamp } from 'firebase/firestore'
import FeedbackForm from '@/components/feedback/FeedbackForm.vue'
import MainPageShell from '@/components/layout/MainPageShell.vue'

const suggestion = ref('')
const submitted = ref(false)
const favoritePart = ref('')
const errorFeedback = ref('')
const screenshotBase64 = ref('')

const currentUser = ref<User | null>(null)
onMounted(() => {
  onAuthStateChanged(auth, (user) => {
    if (user) {
      currentUser.value = user
    } else {
      currentUser.value = null
    }
  })
})

const handleSubmit = async () => {
  if (!errorFeedback.value || !favoritePart.value || !suggestion.value) {
    alert('請完整填寫所有欄位')
    return
  }

  if (!currentUser.value) {
    alert('請先登入帳號再提交回饋')
    return
  }

  const payload = {
    uid: currentUser.value?.uid,
    suggestion: suggestion.value,
    favoritePart: favoritePart.value,
    errorFeedback: errorFeedback.value,
    screenshotBase64: screenshotBase64.value,
    createdAt: serverTimestamp(),
  }

  try {
    await addDoc(collection(db, 'feedback'), payload)
    submitted.value = true
    alert('提交成功，感謝你的回饋！')
    errorFeedback.value = ''
    favoritePart.value = ''
    suggestion.value = ''
    screenshotBase64.value = ''
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : String(err)
    console.error('提交失敗:', msg)
    alert('提交失敗，請稍後再試')
  }
}
</script>

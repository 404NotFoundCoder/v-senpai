import { updateMessageFeedback } from '@/composables/services/chatFirestoreService'
import { ref } from 'vue'

export function useFeedback() {
  const showFeedback = ref(false)
  const feedbackGiven = ref(false)
  const showMetadataDialog = ref(false)

  const toggleFeedback = () => {
    showFeedback.value = !showFeedback.value
  }

  const giveFeedback = async (userId: string, messageId: string, type: 'like' | 'dislike') => {
    try {
      await updateMessageFeedback(userId, messageId, type)
      feedbackGiven.value = true
      showFeedback.value = false
    } catch (error) {
      console.error('❌ 回饋失敗:', error)
    }
  }

  return {
    showFeedback,
    feedbackGiven,
    showMetadataDialog,
    toggleFeedback,
    giveFeedback,
  }
}

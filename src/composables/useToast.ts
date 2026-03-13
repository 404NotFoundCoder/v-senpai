import { ref } from 'vue'

export type ToastType = 'success' | 'info'

export interface ToastState {
  visible: boolean
  message: string
  type: ToastType
}

const toastState = ref<ToastState>({
  visible: false,
  message: '',
  type: 'success',
})

let hideTimer: ReturnType<typeof setTimeout> | null = null

export function useToast() {
  function showToast(message: string, type: ToastType = 'success') {
    if (hideTimer) clearTimeout(hideTimer)
    toastState.value = { visible: true, message, type }
    hideTimer = setTimeout(() => {
      hide()
      hideTimer = null
    }, 3500)
  }

  function hide() {
    toastState.value = { ...toastState.value, visible: false }
  }

  return { toastState, showToast, hide }
}

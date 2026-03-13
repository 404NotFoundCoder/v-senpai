<template>
  <Teleport to="body">
    <Transition name="toast-slide">
      <div
        v-if="toastState.visible"
        class="toast-bar"
        :class="[`toast--${toastState.type}`]"
        role="alert"
      >
        <span class="toast-icon">{{ toastState.type === 'success' ? '✓' : '💬' }}</span>
        <span class="toast-message">{{ toastState.message }}</span>
        <button
          type="button"
          class="toast-close"
          aria-label="關閉"
          @click="hide"
        >
          ×
        </button>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { useToast } from '@/composables/useToast'

const { toastState, hide } = useToast()
</script>

<style scoped>
.toast-bar {
  position: fixed;
  top: 3.5rem;
  left: 50%;
  transform: translateX(-50%);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 0.875rem 1.5rem;
  margin: 0 auto;
  max-width: 36rem;
  width: calc(100% - 2rem);
  border-radius: 0 0 1rem 1rem;
  font-size: 0.9375rem;
  font-weight: 600;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
}
.toast--success {
  background: linear-gradient(135deg, #059669 0%, #10b981 100%);
  color: #fff;
}
.toast--success .toast-icon {
  background: rgba(255, 255, 255, 0.25);
  color: #fff;
}
.toast--success .toast-close {
  background: rgba(255, 255, 255, 0.2);
  color: #fff;
}
.toast--success .toast-close:hover {
  background: rgba(255, 255, 255, 0.35);
}
.toast--info {
  background: linear-gradient(135deg, #ea580c 0%, #f97316 100%);
  color: #fff;
}
.toast--info .toast-icon {
  background: rgba(255, 255, 255, 0.25);
  color: #fff;
}
.toast--info .toast-close {
  background: rgba(255, 255, 255, 0.2);
  color: #fff;
}
.toast--info .toast-close:hover {
  background: rgba(255, 255, 255, 0.35);
}
.toast-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 1.5rem;
  height: 1.5rem;
  border-radius: 50%;
  font-size: 0.875rem;
  font-weight: 700;
  flex-shrink: 0;
}
.toast-message {
  flex: 1;
  text-align: center;
  letter-spacing: 0.02em;
}
.toast-close {
  flex-shrink: 0;
  width: 1.75rem;
  height: 1.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: 0.375rem;
  font-size: 1.25rem;
  line-height: 1;
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
}
.toast-slide-enter-active,
.toast-slide-leave-active {
  transition: transform 0.3s ease, opacity 0.25s ease;
}
.toast-slide-enter-from,
.toast-slide-leave-to {
  transform: translateX(-50%) translateY(-1rem);
  opacity: 0;
}
.toast-slide-enter-to,
.toast-slide-leave-from {
  transform: translateX(-50%) translateY(0);
  opacity: 1;
}
</style>

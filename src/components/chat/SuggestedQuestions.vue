<template>
  <div class="suggested-outer">
    <!-- FAB（不佔版面） -->
    <button
      v-if="!isOpen"
      type="button"
      class="suggested-fab"
      @click="isOpen = true"
      aria-label="顯示建議問題"
    >
      <span class="suggested-fab-icon" aria-hidden="true">✨</span>
      <span class="suggested-fab-text">建議</span>
    </button>

    <!-- Drawer（只保留隱藏/關閉） -->
    <transition name="suggested-drawer-fade">
      <div v-if="isOpen" class="suggested-drawer-wrap">
        <div class="suggested-drawer" role="dialog" aria-modal="true">
          <div class="suggested-drawer-header">
            <div class="suggested-header-left">
              <span class="suggested-icon" aria-hidden="true">💬</span>
              <div class="suggested-title">
                <div class="font-semibold text-primary-800">建議問題</div>
              </div>
            </div>

            <button type="button" class="suggested-hide" @click="isOpen = false">隱藏</button>
          </div>

          <div class="suggested-body">
            <div v-for="(group, gIndex) in visibleGroups" :key="gIndex" class="suggested-group">
              <div v-if="group.title" class="suggested-group-title">
                {{ group.title }}
              </div>

              <div class="suggested-questions">
                <button
                  v-for="(q, index) in group.questions"
                  :key="index"
                  type="button"
                  class="suggested-chip"
                  @click="selectQuestion(q)"
                >
                  {{ q }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

type QuestionGroup = {
  title?: string
  questions: string[]
}

const props = defineProps<{
  // 舊版相容：只傳 questions 時，也能正常運作
  questions?: string[]
  // 未來擴充：可傳多組建議問題
  groups?: QuestionGroup[]
}>()

const emit = defineEmits<{
  (e: 'select', q: string): void
}>()

const defaultQuestions = [
  '從系統分析與設計課程中遇到什麼問題？如何解決？',
  '使用 git 嗎？',
  '可以給一個報告準備方向嗎？',
]

const isOpen = ref(false)

function selectQuestion(q: string) {
  emit('select', q)
  isOpen.value = false
}

const visibleGroups = computed<QuestionGroup[]>(() => {
  const groups = Array.isArray(props.groups) ? props.groups : []
  if (groups.length > 0) {
    return groups
      .filter((g) => Array.isArray(g.questions) && g.questions.length > 0)
      .map((g) => ({ title: g.title, questions: g.questions }))
  }

  const qs =
    Array.isArray(props.questions) && props.questions.length > 0
      ? props.questions
      : defaultQuestions
  return [{ title: undefined, questions: qs }]
})
</script>

<style scoped>
.suggested-outer {
  width: 100%;
  position: relative;
}

/* 方案A：右下角 FAB + 抽屜 drawer */
.suggested-fab {
  position: absolute;
  right: 1rem;
  bottom: calc(0.75rem + env(safe-area-inset-bottom));
  z-index: 61;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.65rem 1rem;
  background: #a76f65;
  color: #fff;
  border: none;
  border-radius: 9999px;
  font-weight: 800;
  cursor: pointer;
  box-shadow: 0 18px 50px rgba(63, 40, 37, 0.18);
  transition:
    transform 0.12s ease,
    background 0.2s ease;
}

.suggested-fab:hover {
  background: #87564d;
  transform: translateY(-1px);
}

.suggested-fab-icon {
  width: 1.25rem;
  height: 1.25rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.suggested-fab-text {
  font-size: 0.95rem;
  letter-spacing: 0.02em;
}

.suggested-drawer-wrap {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 61;
  display: flex;
  justify-content: flex-end;
}

.suggested-drawer {
  position: relative;
  background: #fdf7f0; /* primary-50 */
  border: 1px solid rgba(167, 111, 101, 0.18);
  border-radius: 1.25rem;
  box-shadow: 0 30px 80px rgba(0, 0, 0, 0.18);
  max-height: 65vh;
  overflow-y: auto;
  padding: 1rem;
  width: 100%;
  margin: 0 1rem;
  animation: suggested-drawer-in 0.22s ease-out;
}

@keyframes suggested-drawer-in {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.suggested-drawer-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 0.5rem;
}

@media (max-width: 639px) {
  .suggested-fab-text {
    display: none;
  }
  .suggested-fab {
    padding: 0.7rem;
  }
}

@media (min-width: 768px) {
  .suggested-drawer {
    width: 28rem;
    max-height: 65vh;
    margin-left: auto;
    margin-right: 1.25rem;
  }
}

.suggested-drawer-fade-enter-active,
.suggested-drawer-fade-leave-active {
  transition:
    opacity 0.18s ease,
    transform 0.18s ease;
}
.suggested-drawer-fade-enter-from,
.suggested-drawer-fade-leave-to {
  opacity: 0;
  transform: translateY(6px);
}

.suggested-card {
  background: #fdf7f0; /* primary-50 */
  border: 1px solid rgba(167, 111, 101, 0.18);
  border-radius: 1rem;
  padding: 0.75rem 1rem;
  box-shadow: 0 6px 18px rgba(63, 40, 37, 0.06);
}

.suggested-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 0.5rem;
}

.suggested-header-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.suggested-icon {
  width: 2rem;
  height: 2rem;
  border-radius: 9999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: rgba(167, 111, 101, 0.18);
  color: #87564d; /* primary-700 */
  font-weight: 700;
  flex-shrink: 0;
}

.suggested-title {
  display: flex;
  flex-direction: column;
}

.suggested-header-right {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-shrink: 0;
}

.suggested-link {
  border: none;
  background: transparent;
  color: #a76f65; /* primary-600 */
  font-weight: 600;
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  border-radius: 0.5rem;
  transition: background 0.2s ease;
}
.suggested-link:hover {
  background: rgba(167, 111, 101, 0.12);
}

.suggested-hide {
  border: none;
  background: rgba(201, 146, 136, 0.18);
  color: #654039;
  font-weight: 600;
  cursor: pointer;
  padding: 0.25rem 0.6rem;
  border-radius: 0.6rem;
  transition: background 0.2s ease;
}
.suggested-hide:hover {
  background: rgba(201, 146, 136, 0.26);
}

.suggested-collapse-enter-active,
.suggested-collapse-leave-active {
  transition:
    opacity 0.2s ease,
    transform 0.2s ease;
}
.suggested-collapse-enter-from,
.suggested-collapse-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

.suggested-body {
  padding-top: 0.35rem;
}

.suggested-group + .suggested-group {
  margin-top: 0.75rem;
  padding-top: 0.75rem;
  border-top: 1px dashed rgba(167, 111, 101, 0.25);
}

.suggested-group-title {
  font-size: 0.875rem;
  font-weight: 700;
  color: #654039; /* primary-800 */
  margin-bottom: 0.5rem;
}

.suggested-questions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

/* 手機：改成水平滑動，避免高度被拉太高 */
@media (max-width: 639px) {
  .suggested-questions {
    flex-wrap: nowrap;
    overflow-x: auto;
    padding-bottom: 0.25rem;
    -webkit-overflow-scrolling: touch;
  }

  /* 手機：維持單行 chip，搭配外層水平滑動 */
  .suggested-chip {
    white-space: nowrap;
    text-align: center;
  }
}

.suggested-chip {
  background: rgba(251, 236, 220, 0.95); /* primary-100-ish */
  border: 1px solid rgba(201, 146, 136, 0.25);
  color: #654039; /* primary-800 */
  font-size: 0.9rem;
  font-weight: 600;
  padding: 0.45rem 0.75rem;
  border-radius: 9999px;
  cursor: pointer;
  transition:
    transform 0.12s ease,
    background 0.2s ease,
    border-color 0.2s ease;
  /* 桌機：允許換行，避免最後一個字被截掉 */
  white-space: normal;
  overflow-wrap: anywhere;
  word-break: break-word;
  text-align: left;
}

.suggested-chip:hover {
  background: rgba(249, 216, 193, 0.95); /* primary-100-ish / warm */
  border-color: rgba(167, 111, 101, 0.45);
  transform: translateY(-1px);
}

.suggested-hiddenbar {
  display: flex;
  justify-content: center;
}
.suggested-hidden-chip {
  background: rgba(167, 111, 101, 0.12);
  border: 1px solid rgba(167, 111, 101, 0.22);
  color: #87564d;
  font-weight: 700;
  padding: 0.5rem 0.9rem;
  border-radius: 9999px;
  cursor: pointer;
  transition:
    background 0.2s ease,
    transform 0.12s ease;
}
.suggested-hidden-chip:hover {
  background: rgba(167, 111, 101, 0.18);
  transform: translateY(-1px);
}
</style>

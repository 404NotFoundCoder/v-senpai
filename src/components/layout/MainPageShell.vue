<template>
  <!-- 與 ChatView 相同策略：外層限高，僅此槽內捲動 → Footer 固定在視窗底、不會「浮起」 -->
  <div class="flex h-full min-h-0 min-w-0 flex-col">
    <div class="main-page-scroll flex-1 min-h-0 overflow-y-auto">
      <slot />
    </div>
  </div>
</template>

<style scoped>
.main-page-scroll {
  -webkit-overflow-scrolling: touch;
  overscroll-behavior-y: contain;
}
</style>

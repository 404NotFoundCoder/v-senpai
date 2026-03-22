<template>
  <MainPageShell>
    <div class="mx-3 px-4 pb-10 pt-16 sm:max-w-4xl">
      <UserProfileSettings />
      <hr class="divider" />
      <UserTestSignupForm />
    </div>
  </MainPageShell>
</template>

<script setup lang="ts">
import MainPageShell from '@/components/layout/MainPageShell.vue'
import UserTestSignupForm from '../components/personal/UserTestSignupForm.vue'
import UserProfileSettings from '../components/personal/UserProfileSettings.vue'
</script>

<style scoped></style>

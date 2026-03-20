import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import './config/firebaseConfig'
import { loginForumFromQueryToken } from './utils/forumAuth'

async function bootstrap() {
  // 先處理 customToken 自動登入，避免被 router guard 提前導回
  await loginForumFromQueryToken()

  const app = createApp(App)
  app.use(createPinia())
  app.use(router)

  // 雙保險：router 初始化後再清一次 t，避免初始 route state 帶回 query
  await router.isReady()
  const current = router.currentRoute.value
  if (current.query.t !== undefined) {
    const { t: _t, ...restQuery } = current.query
    await router.replace({
      path: current.path,
      query: restQuery,
      hash: current.hash,
    })
  }

  app.mount('#app')
}

bootstrap()

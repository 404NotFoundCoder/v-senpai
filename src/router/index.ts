import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import { onAuthStateChanged, getAuth } from 'firebase/auth'
import { getDoc, doc } from 'firebase/firestore'
import { auth, db } from '@/config/firebaseConfig'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    {
      path: '/chat',
      name: 'chat',
      component: () => import('../views/ChatView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/feedback',
      name: 'feedback',
      component: () => import('../views/FeedbackView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/personal',
      name: 'personal',
      component: () => import('../views/PersonalView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/feedback-review',
      component: () => import('@/views/FeedbackReviewView.vue'),
      meta: { requiresAuth: true, requiresAdmin: true },
    },
    {
      path: '/signup-list',
      name: 'signup-list',
      component: () => import('@/views/SignupListView.vue'),
      meta: { requiresAuth: true, requiresAdmin: true },
    },
    {
      path: '/user-messages/:uid',
      name: 'user-messages',
      component: () => import('@/views/UserMessagesView.vue'),
      meta: { requiresAuth: true, requiresAdmin: true },
    },
    {
      path: '/dislike-feedback-export',
      name: 'dislike-feedback-export',
      component: () => import('@/views/DislikeFeedbackExportView.vue'),
      meta: { requiresAuth: true },
      // meta: { requiresAuth: true, requiresAdmin: true },
    },
  ],
})

// 快取目前使用者
let currentUser: any = null
onAuthStateChanged(auth, (user) => {
  currentUser = user
})

// 檢查是否為 admin
const isAdmin = async (uid: string) => {
  try {
    const docSnap = await getDoc(doc(db, 'users', uid))
    return docSnap.exists() && docSnap.data().role === 'admin'
  } catch (err) {
    console.error('讀取使用者角色錯誤：', err)
    return false
  }
}

router.beforeEach(async (to, from, next) => {
  const auth = getAuth()

  if (!auth.currentUser) {
    await new Promise((resolve) => onAuthStateChanged(auth, resolve))
  }

  const user = auth.currentUser

  // 未登入但進入需要登入的頁面
  if (to.meta.requiresAuth && !user) {
    return next('/')
  }

  // 權限不足
  if (to.meta.requiresAdmin && user) {
    const isUserAdmin = await isAdmin(user.uid)
    if (!isUserAdmin) {
      return next('/')
    }
  }

  return next()
})

export default router

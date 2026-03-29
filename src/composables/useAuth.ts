import { ref, onMounted } from 'vue'
import { auth, db } from '../config/firebaseConfig'
import { signInWithPopup, GithubAuthProvider, onAuthStateChanged, signOut } from 'firebase/auth'
import { doc, getDoc, setDoc, updateDoc } from 'firebase/firestore'
import type { User } from 'firebase/auth'
import { useRouter } from 'vue-router'

const user = ref<User | null>(null)
const provider = new GithubAuthProvider()

export function useAuth() {
  const router = useRouter()

  const signInWithGitHub = async () => {
    try {
      const result = await signInWithPopup(auth, provider)
      const credential = GithubAuthProvider.credentialFromResult(result)
      const accessToken = credential?.accessToken
      const userInfo = result.user

      const userRef = doc(db, 'users', userInfo.uid)
      const userSnap = await getDoc(userRef)

      if (userSnap.exists()) {
        await updateDoc(userRef, { accessToken })
        console.log('exists updateUserDoc')
      } else {
        await setDoc(userRef, {
          username: userInfo.displayName,
          email: userInfo.email,
          accessToken,
          priority: false,
          createdAt: new Date(),
          role: 'user',
        })
        console.log('non exists setUserDoc')
      }

      user.value = userInfo
      console.log('User 已登入:', user.value)
    } catch (error: any) {
      console.error('🔥 原始錯誤:', error)

      if (error?.code) {
        console.error('錯誤碼:', error.code)
      }

      if (error?.message) {
        console.error('錯誤訊息:', error.message)
      }
    }
  }

  const logout = async () => {
    await signOut(auth)
    user.value = null
    router.push('/')
  }

  onMounted(() => {
    onAuthStateChanged(auth, (firebaseUser) => {
      user.value = firebaseUser
    })
  })

  return {
    user,
    signInWithGitHub,
    logout,
  }
}

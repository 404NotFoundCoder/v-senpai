import { getAuth, signInWithCustomToken } from 'firebase/auth'
import { FORUM_ORIGIN, VERIFY_API_URL } from '@/config/envEndpoints'

async function exchangeToCustomToken(idToken: string): Promise<string> {
  const response = await fetch(VERIFY_API_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ idToken }),
  })

  if (!response.ok) {
    throw new Error(`verify API 失敗: ${response.status}`)
  }

  const data = (await response.json()) as { customToken?: string }
  if (!data?.customToken) {
    throw new Error('verify API 未回傳 customToken')
  }

  return data.customToken
}

export async function buildForumUrl(
  path: string = '/',
  extraParams?: Record<string, string>,
): Promise<string> {
  const url = new URL(path, FORUM_ORIGIN)

  if (extraParams) {
    Object.entries(extraParams).forEach(([k, v]) => {
      url.searchParams.set(k, v)
    })
  }

  const user = getAuth().currentUser
  if (!user) {
    throw new Error('尚未登入，無法建立論壇登入連結')
  }

  const idToken = await user.getIdToken()
  const customToken = await exchangeToCustomToken(idToken)

  // query key 使用 t（依需求），此處帶 customToken
  url.searchParams.set('t', customToken)

  return url.toString()
}

export async function goForum(path: string = '/', extraParams?: Record<string, string>) {
  const url = await buildForumUrl(path, extraParams)
  window.location.href = url
}

/**
 * B 網站使用：從 query 的 t(customToken) 自動登入 Firebase。
 * - 會先把 URL 的 t 清掉，再嘗試登入。
 */
export async function loginForumFromQueryToken() {
  const url = new URL(window.location.href)
  const token = url.searchParams.get('t')
  if (!token) return

  // 優先清理 URL，避免 token 外露在網址列與歷史紀錄
  url.searchParams.delete('t')
  window.history.replaceState({}, '', url.toString())

  const auth = getAuth()

  try {
    if (auth.currentUser) {
      console.log('ℹ️ 已登入，略過 customToken 自動登入')
      return
    }
    await signInWithCustomToken(auth, token)
    console.log('✅ customToken 自動登入成功')
  } catch (error) {
    console.error('❌ customToken 自動登入失敗:', error)
  }
}

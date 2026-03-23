const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'

export const FORUM_ORIGIN = isLocalhost ? 'http://localhost:3000' : 'https://sa-forum.vercel.app'

export const API_BASE_URL = isLocalhost ? 'http://localhost:5000' : ''

export const CHAT_API_URL = `${API_BASE_URL}/api/chat`
export const DRAFT_API_URL = `${API_BASE_URL}/api/draft`
export const VERIFY_API_URL = `${API_BASE_URL}/api/verify`

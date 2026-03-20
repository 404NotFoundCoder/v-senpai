export function formatChatTimestamp(input?: string | Date | null): string {
  if (!input) return ''

  const date = input instanceof Date ? input : new Date(input)
  if (Number.isNaN(date.getTime())) return String(input)

  return date.toLocaleString('zh-TW', {
    year: 'numeric',
    month: 'numeric',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  })
}

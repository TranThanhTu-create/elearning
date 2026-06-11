export function formatVnd(amount: number | null | undefined): string {
  if (amount == null) return '0 ₫'
  if (amount === 0) return 'Miễn phí'
  return amount.toLocaleString('vi-VN') + ' ₫'
}

export function formatVndRaw(amount: number | null | undefined): string {
  if (amount == null || amount === 0) return '0 ₫'
  return amount.toLocaleString('vi-VN') + ' ₫'
}

export function formatDate(iso: string | null | undefined): string {
  if (!iso) return '—'
  return new Date(iso).toLocaleDateString('vi-VN', {
    timeZone: 'Asia/Ho_Chi_Minh',
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  })
}

export function formatDateTime(iso: string | null | undefined): string {
  if (!iso) return '—'
  return new Date(iso).toLocaleString('vi-VN', {
    timeZone: 'Asia/Ho_Chi_Minh',
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function formatDuration(seconds: number | null | undefined): string {
  if (!seconds) return '0 phút'
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  if (h > 0) return `${h} giờ ${m} phút`
  return `${m} phút`
}

export function formatNumber(n: number | null | undefined): string {
  if (n == null) return '0'
  return n.toLocaleString('vi-VN')
}

export function slugify(text: string): string {
  return text
    .toLowerCase()
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '')
    .replace(/[^a-z0-9\s-]/g, '')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .trim()
}

export function getInitials(name: string): string {
  return name
    .split(' ')
    .filter(Boolean)
    .map((w) => w[0].toUpperCase())
    .slice(0, 2)
    .join('')
}

export function starRating(rating: number): string {
  const full = Math.floor(rating)
  const half = rating - full >= 0.5
  return '★'.repeat(full) + (half ? '½' : '') + '☆'.repeat(5 - full - (half ? 1 : 0))
}

export function clsx(...classes: (string | undefined | null | false)[]): string {
  return classes.filter(Boolean).join(' ')
}

export function getStatusTag(status: string): string {
  const map: Record<string, string> = {
    completed: 'tag-success',
    published: 'tag-success',
    active: 'tag-success',
    approved: 'tag-success',
    paid: 'tag-success',
    pending: 'tag-pending',
    processing: 'tag-pending',
    draft: 'tag-default',
    inactive: 'tag-default',
    failed: 'tag-danger',
    refunded: 'tag-danger',
    expired: 'tag-danger',
    rejected: 'tag-danger',
    cancelled: 'tag-danger',
  }
  return map[status] ?? 'tag-default'
}

export function timeAgo(iso: string | null | undefined): string {
  if (!iso) return ''
  const diff = Date.now() - new Date(iso).getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return 'vừa xong'
  if (mins < 60) return `${mins} phút trước`
  const hours = Math.floor(mins / 60)
  if (hours < 24) return `${hours} giờ trước`
  const days = Math.floor(hours / 24)
  if (days < 30) return `${days} ngày trước`
  return formatDate(iso)
}

export function truncate(text: string, maxLen: number): string {
  if (text.length <= maxLen) return text
  return text.slice(0, maxLen).trimEnd() + '...'
}

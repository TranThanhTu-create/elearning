'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/lib/auth'
import { api } from '@/lib/api'
import { formatVnd } from '@/lib/utils'
import type { Course } from '@/types'

interface Props {
  course: Course
}

export default function CourseBuyHeroBtn({ course }: Props) {
  const { user } = useAuth()
  const router = useRouter()
  const [loading, setLoading] = useState(false)

  const handleBuy = async () => {
    if (!user) { router.push(`/login?redirect=/courses/${course.slug}`); return }
    if (course.is_enrolled) { router.push(`/learn/${course.slug}`); return }
    setLoading(true)
    try {
      const p = new URLSearchParams(window.location.search)
      const { data } = await api.post('/orders/create', {
        course_id: course.id,
        utm_source: p.get('utm_source') || undefined,
        utm_medium: p.get('utm_medium') || undefined,
        utm_campaign: p.get('utm_campaign') || undefined,
      })
      router.push(`/checkout/${data.order_code}`)
    } catch {
      alert('Có lỗi xảy ra, vui lòng thử lại')
    } finally {
      setLoading(false)
    }
  }

  const isFree = course.price === 0

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '16px', flexWrap: 'wrap' }}>
      <button
        className="btn btn-primary btn-xl"
        onClick={handleBuy}
        disabled={loading}
        style={{ minWidth: '220px', fontSize: '17px', fontWeight: 900, letterSpacing: '0.3px' }}
      >
        {loading ? <span className="spinner" /> :
         course.is_enrolled ? '▶ Tiếp tục học ngay' :
         isFree ? '🚀 Đăng ký miễn phí' :
         `🛒 Đăng ký — ${formatVnd(course.price)}`}
      </button>
      {isFree ? null : (
        <span style={{ fontSize: '13px', color: 'var(--text-dim)' }}>🛡️ Hoàn tiền 100% trong 7 ngày</span>
      )}
    </div>
  )
}

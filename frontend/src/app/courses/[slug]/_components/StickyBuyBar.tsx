'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/lib/auth'
import { api, extractError } from '@/lib/api'
import type { Course } from '@/types'

interface Props {
  course: Course
}

export default function StickyBuyBar({ course }: Props) {
  const { user } = useAuth()
  const router = useRouter()
  const [visible, setVisible] = useState(false)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    const onScroll = () => setVisible(window.scrollY > 480)
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

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
      })
      router.push(`/checkout/${data.order_code}`)
    } catch (e: unknown) {
      alert(e instanceof Error ? e.message : 'Có lỗi xảy ra')
    } finally {
      setLoading(false)
    }
  }

  const formatVnd = (n: number) => n.toLocaleString('vi-VN') + ' ₫'

  return (
    <div style={{
      position: 'fixed', top: 0, left: 0, right: 0, zIndex: 999,
      background: 'rgba(7,11,20,0.96)', backdropFilter: 'blur(16px)',
      borderBottom: '1px solid rgba(0,212,255,0.2)',
      boxShadow: '0 4px 24px rgba(0,0,0,0.4)',
      transform: visible ? 'translateY(0)' : 'translateY(-100%)',
      transition: 'transform 0.3s cubic-bezier(0.4,0,0.2,1)',
      padding: '10px 24px',
    }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '16px', flexWrap: 'wrap' }}>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ fontWeight: 700, fontSize: '14px', color: 'var(--text)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
            {course.title}
          </div>
          {course.avg_rating > 0 && (
            <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '2px' }}>
              ⭐ {course.avg_rating.toFixed(1)} · {course.total_students || 0} học viên
            </div>
          )}
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px', flexShrink: 0 }}>
          {course.original_price && course.original_price > course.price && (
            <span style={{ fontSize: '13px', color: 'var(--text-dim)', textDecoration: 'line-through' }}>
              {formatVnd(course.original_price)}
            </span>
          )}
          <span style={{ fontSize: '22px', fontWeight: 900, color: 'var(--text)' }}>
            {course.price === 0 ? 'Miễn phí' : formatVnd(course.price)}
          </span>
          <button
            className="btn btn-primary btn-lg"
            onClick={handleBuy}
            disabled={loading}
            style={{ minWidth: '140px' }}
          >
            {loading ? <span className="spinner" /> :
             course.is_enrolled ? '▶ Học ngay' :
             course.price === 0 ? '🚀 Đăng ký' :
             '🛒 Mua ngay'}
          </button>
        </div>
      </div>
    </div>
  )
}

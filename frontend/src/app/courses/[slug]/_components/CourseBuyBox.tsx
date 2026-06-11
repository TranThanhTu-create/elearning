'use client'

import { useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/lib/auth'
import { api, extractError } from '@/lib/api'
import { formatVnd, formatDuration } from '@/lib/utils'
import type { Course } from '@/types'

function levelLabel(level: string) {
  return { beginner: 'Cơ bản', intermediate: 'Trung cấp', advanced: 'Nâng cao' }[level] ?? level
}

interface Props {
  course: Course
  totalLessons: number
  totalDuration: number
}

export default function CourseBuyBox({ course, totalLessons, totalDuration }: Props) {
  const { user } = useAuth()
  const router = useRouter()
  const [enrolling, setEnrolling] = useState(false)
  const [error, setError] = useState('')

  const handleBuy = async () => {
    if (!user) { router.push(`/login?redirect=/courses/${course.slug}`); return }
    if (course.is_enrolled) { router.push(`/learn/${course.slug}`); return }
    setEnrolling(true)
    try {
      const params = new URLSearchParams(window.location.search)
      const { data } = await api.post('/orders/create', {
        course_id: course.id,
        utm_source: params.get('utm_source') || undefined,
        utm_medium: params.get('utm_medium') || undefined,
        utm_campaign: params.get('utm_campaign') || undefined,
      })
      router.push(`/checkout/${data.order_code}`)
    } catch (err) {
      setError(extractError(err))
    } finally {
      setEnrolling(false)
    }
  }

  return (
    <div style={{ position: 'sticky', top: '80px' }}>
      <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border-bright)', borderRadius: '16px', padding: '24px', boxShadow: '0 0 40px rgba(0,212,255,0.08)' }}>
        {course.thumbnail_url && (
          <img src={course.thumbnail_url} alt={course.title} style={{ width: '100%', borderRadius: '10px', marginBottom: '16px', aspectRatio: '16/9', objectFit: 'cover' }} />
        )}
        <div style={{ marginBottom: '8px' }}>
          <span style={{ fontSize: '30px', fontWeight: 900, color: 'var(--text)' }}>
            {course.price === 0 ? 'Miễn phí' : formatVnd(course.price)}
          </span>
          {course.original_price && course.original_price > course.price && (
            <span style={{ fontSize: '16px', color: 'var(--text-dim)', textDecoration: 'line-through', marginLeft: '10px' }}>
              {formatVnd(course.original_price)}
            </span>
          )}
        </div>
        {course.discount_percent && course.discount_percent > 0 ? (
          <div style={{ fontSize: '13px', color: '#ff4757', fontWeight: 700, marginBottom: '12px' }}>
            🔥 Tiết kiệm {course.discount_percent}%
          </div>
        ) : null}
        {error && <div className="alert alert-error" style={{ marginBottom: '12px' }}>{error}</div>}
        <button className="btn btn-primary btn-full btn-lg" onClick={handleBuy} disabled={enrolling} style={{ marginBottom: '12px' }}>
          {enrolling ? <span className="spinner" /> : course.is_enrolled ? '▶ Tiếp tục học' : course.price === 0 ? 'Đăng ký miễn phí' : '🛒 Mua ngay'}
        </button>
        {!user && (
          <p style={{ fontSize: '12px', color: 'var(--text-dim)', textAlign: 'center' }}>
            Cần <Link href="/login" style={{ color: 'var(--neon)', textDecoration: 'none' }}>đăng nhập</Link> để mua khóa học
          </p>
        )}
        <div style={{ marginTop: '16px', borderTop: '1px solid var(--border)', paddingTop: '16px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {([
            ['📹', `${totalLessons} bài học`],
            ['⏱️', formatDuration(totalDuration)],
            ['📊', levelLabel(course.level || '')],
            ['🌐', course.language === 'vi' ? 'Tiếng Việt' : (course.language || 'Tiếng Việt')],
            ['♾️', 'Truy cập trọn đời'],
          ] as [string, string][]).map(([icon, text]) => (
            <div key={text} style={{ display: 'flex', gap: '10px', fontSize: '14px', color: 'var(--text-muted)', alignItems: 'center' }}>
              <span>{icon}</span><span>{text}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

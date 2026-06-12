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
    setEnrolling(true); setError('')
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

  const isFree = course.price === 0
  const hasDiscount = course.original_price && course.original_price > course.price

  return (
    <div style={{ position: 'sticky', top: '80px' }}>
      <div style={{
        background: 'var(--bg-card)',
        border: '1px solid rgba(0,212,255,0.25)',
        borderRadius: '16px',
        overflow: 'hidden',
        boxShadow: '0 0 60px rgba(0,212,255,0.08)',
      }}>
        {/* Thumbnail */}
        {course.thumbnail_url && (
          <div style={{ position: 'relative' }}>
            <img src={course.thumbnail_url} alt={course.title} style={{ width: '100%', aspectRatio: '16/9', objectFit: 'cover', display: 'block' }} />
            {course.badge && (
              <span style={{ position: 'absolute', top: '10px', left: '10px', background: '#f59e0b', color: '#000', fontSize: '11px', fontWeight: 800, padding: '3px 9px', borderRadius: '5px', letterSpacing: '0.5px' }}>
                {course.badge.toUpperCase()}
              </span>
            )}
          </div>
        )}

        <div style={{ padding: '20px' }}>
          {/* Price */}
          <div style={{ marginBottom: '14px' }}>
            {isFree ? (
              <div style={{ fontSize: '32px', fontWeight: 900, color: '#00ff88' }}>Miễn phí</div>
            ) : (
              <>
                <div style={{ display: 'flex', alignItems: 'baseline', gap: '10px', flexWrap: 'wrap' }}>
                  <span style={{ fontSize: '34px', fontWeight: 900, color: 'var(--text)', letterSpacing: '-0.5px' }}>{formatVnd(course.price)}</span>
                  {hasDiscount && (
                    <span style={{ fontSize: '17px', color: 'var(--text-dim)', textDecoration: 'line-through' }}>
                      {formatVnd(course.original_price!)}
                    </span>
                  )}
                </div>
                {course.discount_percent && course.discount_percent > 0 ? (
                  <div style={{ marginTop: '4px', fontSize: '13px', color: '#ff6b6b', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '5px' }}>
                    🔥 Tiết kiệm <strong>{course.discount_percent}%</strong> — Ưu đãi có hạn
                  </div>
                ) : null}
              </>
            )}
          </div>

          {/* Error */}
          {error && (
            <div className="alert alert-error" style={{ marginBottom: '12px', fontSize: '13px' }}>{error}</div>
          )}

          {/* CTA button */}
          <button
            className="btn btn-primary btn-full btn-lg"
            onClick={handleBuy}
            disabled={enrolling}
            style={{ marginBottom: '10px', fontSize: '16px', fontWeight: 800, letterSpacing: '0.3px', height: '52px' }}
          >
            {enrolling ? <span className="spinner" /> :
             course.is_enrolled ? '▶ Tiếp tục học ngay' :
             isFree ? '🚀 Đăng ký miễn phí' :
             '🛒 Mua ngay'}
          </button>

          {!user && (
            <p style={{ fontSize: '12px', color: 'var(--text-dim)', textAlign: 'center', marginBottom: '10px' }}>
              Cần <Link href="/login" style={{ color: 'var(--neon)', textDecoration: 'none', fontWeight: 600 }}>đăng nhập</Link> để mua khóa học
            </p>
          )}

          {/* Guarantee */}
          <div style={{ textAlign: 'center', fontSize: '12px', color: 'var(--text-dim)', marginBottom: '16px', padding: '8px', background: 'rgba(0,255,136,0.04)', borderRadius: '8px', border: '1px solid rgba(0,255,136,0.1)' }}>
            🛡️ Đảm bảo hoàn tiền trong 7 ngày nếu không hài lòng
          </div>

          {/* Divider */}
          <div style={{ borderTop: '1px solid var(--border)', paddingTop: '16px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <p style={{ fontSize: '12px', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.8px', marginBottom: '4px' }}>Khóa học bao gồm</p>
            {([
              ['📹', `${totalLessons} bài học video`],
              ...(totalDuration > 0 ? [['⏱️', formatDuration(totalDuration) + ' nội dung']] : []),
              ['♾️', 'Truy cập trọn đời'],
              ['📱', 'Học trên mọi thiết bị'],
              ['🏆', 'Chứng chỉ hoàn thành'],
              ...(course.level ? [['📊', levelLabel(course.level)]] : []),
              ['🌐', course.language === 'vi' ? 'Tiếng Việt' : (course.language || 'Tiếng Việt')],
            ] as [string, string][]).map(([icon, text]) => (
              <div key={text} style={{ display: 'flex', gap: '10px', fontSize: '13px', color: 'var(--text-muted)', alignItems: 'center' }}>
                <span style={{ fontSize: '15px', width: '20px', textAlign: 'center' }}>{icon}</span>
                <span>{text}</span>
              </div>
            ))}
          </div>

          {/* Share */}
          <div style={{ marginTop: '16px', borderTop: '1px solid var(--border)', paddingTop: '12px', textAlign: 'center' }}>
            <span style={{ fontSize: '12px', color: 'var(--text-dim)' }}>Chia sẻ cho bạn bè:</span>
            <div style={{ display: 'flex', justifyContent: 'center', gap: '10px', marginTop: '8px' }}>
              {[
                { label: 'Facebook', bg: '#1877f2', href: `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(SITE_URL + '/courses/' + course.slug)}` },
                { label: 'Zalo', bg: '#0068ff', href: `https://zalo.me/share/?url=${encodeURIComponent(SITE_URL + '/courses/' + course.slug)}` },
              ].map(s => (
                <a key={s.label} href={s.href} target="_blank" rel="noopener noreferrer"
                  style={{ display: 'inline-flex', alignItems: 'center', padding: '5px 12px', borderRadius: '6px', background: s.bg, color: '#fff', fontSize: '12px', fontWeight: 700, textDecoration: 'none', transition: 'opacity 0.15s' }}
                  onMouseOver={e => (e.currentTarget.style.opacity = '0.85')}
                  onMouseOut={e => (e.currentTarget.style.opacity = '1')}
                >
                  {s.label}
                </a>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || 'https://tumarketing.vn'

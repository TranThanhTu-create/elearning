'use client'

import { useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/lib/auth'
import { api, extractError } from '@/lib/api'
import { formatVnd, formatDuration } from '@/lib/utils'
import type { Course } from '@/types'

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

  const includes = [
    ['📹', `${totalLessons} bài học video`],
    ...(totalDuration > 0 ? [['⏱️', formatDuration(totalDuration) + ' nội dung']] : []),
    ['♾️', 'Truy cập trọn đời'],
    ['📱', 'Học trên mọi thiết bị'],
    ['🏆', 'Chứng chỉ hoàn thành'],
    ['🌐', course.language === 'vi' || !course.language ? 'Tiếng Việt' : course.language],
  ] as [string, string][]

  return (
    <section style={{ padding: '60px 0', background: 'linear-gradient(180deg, var(--bg) 0%, rgba(0,212,255,0.03) 50%, var(--bg) 100%)' }}>
      <div style={{ maxWidth: '640px', margin: '0 auto', padding: '0 24px' }}>

        {/* Heading */}
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <div style={{ display: 'inline-block', background: 'rgba(0,212,255,0.08)', border: '1px solid rgba(0,212,255,0.2)', borderRadius: '20px', padding: '4px 16px', fontSize: '12px', color: 'var(--neon)', fontWeight: 700, letterSpacing: '1px', textTransform: 'uppercase', marginBottom: '14px' }}>
            ĐỀ XUẤT DÀNH CHO BẠN
          </div>
          <h2 style={{ fontSize: '28px', fontWeight: 900, color: 'var(--text)', lineHeight: 1.25 }}>
            Sẵn sàng bắt đầu hành trình?
          </h2>
          <p style={{ fontSize: '15px', color: 'var(--text-muted)', marginTop: '8px' }}>
            Tham gia {course.total_students || 0}+ học viên đang thay đổi sự nghiệp
          </p>
        </div>

        {/* Pricing card */}
        <div style={{
          background: 'var(--bg-card)',
          border: '2px solid rgba(0,212,255,0.3)',
          borderRadius: '20px',
          overflow: 'hidden',
          boxShadow: '0 0 80px rgba(0,212,255,0.12), 0 32px 64px rgba(0,0,0,0.4)',
        }}>
          {/* Thumbnail */}
          {course.thumbnail_url && (
            <div style={{ position: 'relative' }}>
              <img src={course.thumbnail_url} alt={course.title} style={{ width: '100%', aspectRatio: '16/9', objectFit: 'cover', display: 'block' }} />
              {hasDiscount && course.discount_percent && (
                <div style={{ position: 'absolute', top: '14px', right: '14px', background: '#ff4757', color: '#fff', fontSize: '13px', fontWeight: 900, padding: '5px 12px', borderRadius: '8px', letterSpacing: '0.5px' }}>
                  -{course.discount_percent}%
                </div>
              )}
            </div>
          )}

          <div style={{ padding: '28px' }}>
            {/* Price */}
            <div style={{ textAlign: 'center', marginBottom: '20px' }}>
              {isFree ? (
                <div style={{ fontSize: '42px', fontWeight: 900, color: '#00ff88' }}>Miễn phí</div>
              ) : (
                <>
                  <div style={{ display: 'flex', alignItems: 'baseline', gap: '12px', justifyContent: 'center', flexWrap: 'wrap' }}>
                    <span style={{ fontSize: '46px', fontWeight: 900, color: 'var(--text)', letterSpacing: '-1px', lineHeight: 1 }}>
                      {formatVnd(course.price)}
                    </span>
                    {hasDiscount && (
                      <span style={{ fontSize: '20px', color: 'var(--text-dim)', textDecoration: 'line-through' }}>
                        {formatVnd(course.original_price!)}
                      </span>
                    )}
                  </div>
                  {hasDiscount && course.discount_percent && course.discount_percent > 0 && (
                    <div style={{ marginTop: '6px', fontSize: '14px', color: '#ff6b6b', fontWeight: 700 }}>
                      🔥 Tiết kiệm {course.discount_percent}% — Ưu đãi có hạn
                    </div>
                  )}
                </>
              )}
            </div>

            {/* Error */}
            {error && (
              <div className="alert alert-error" style={{ marginBottom: '14px', fontSize: '13px' }}>{error}</div>
            )}

            {/* CTA */}
            <button
              className="btn btn-primary btn-full btn-xl"
              onClick={handleBuy}
              disabled={enrolling}
              style={{ marginBottom: '12px', letterSpacing: '0.5px', fontSize: '17px', fontWeight: 900 }}
            >
              {enrolling ? <span className="spinner" /> :
               course.is_enrolled ? '▶ Tiếp tục học ngay' :
               isFree ? '🚀 Đăng ký miễn phí ngay' :
               '🛒 ĐĂNG KÝ HỌC NGAY'}
            </button>

            {!user && (
              <p style={{ fontSize: '12px', color: 'var(--text-dim)', textAlign: 'center', marginBottom: '14px' }}>
                Cần <Link href="/login" style={{ color: 'var(--neon)', textDecoration: 'none', fontWeight: 600 }}>đăng nhập</Link> để mua khóa học
              </p>
            )}

            {/* Guarantee */}
            <div style={{
              display: 'flex', alignItems: 'center', gap: '10px', justifyContent: 'center',
              padding: '10px', background: 'rgba(0,255,136,0.05)', borderRadius: '10px',
              border: '1px solid rgba(0,255,136,0.15)', marginBottom: '20px',
            }}>
              <span style={{ fontSize: '20px' }}>🛡️</span>
              <span style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
                <strong style={{ color: '#00ff88' }}>Đảm bảo hoàn tiền 100%</strong> trong 7 ngày nếu không hài lòng
              </span>
            </div>

            {/* Course includes */}
            <div style={{ borderTop: '1px solid var(--border)', paddingTop: '18px' }}>
              <p style={{ fontSize: '11px', fontWeight: 800, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '1px', marginBottom: '12px', textAlign: 'center' }}>
                Khóa học bao gồm
              </p>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
                {includes.map(([icon, text]) => (
                  <div key={text} style={{ display: 'flex', gap: '8px', fontSize: '13px', color: 'var(--text-muted)', alignItems: 'center' }}>
                    <span style={{ fontSize: '15px', width: '18px', textAlign: 'center' }}>{icon}</span>
                    <span>{text}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Share */}
            <div style={{ marginTop: '18px', borderTop: '1px solid var(--border)', paddingTop: '14px', textAlign: 'center' }}>
              <span style={{ fontSize: '12px', color: 'var(--text-dim)' }}>Chia sẻ khóa học:</span>
              <div style={{ display: 'flex', justifyContent: 'center', gap: '10px', marginTop: '8px' }}>
                {[
                  { l: 'Facebook', bg: '#1877f2', href: `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent((process.env.NEXT_PUBLIC_SITE_URL || 'https://tumarketing.vn') + '/courses/' + course.slug)}` },
                  { l: 'Zalo', bg: '#0068ff', href: `https://zalo.me/share/?url=${encodeURIComponent((process.env.NEXT_PUBLIC_SITE_URL || 'https://tumarketing.vn') + '/courses/' + course.slug)}` },
                ].map(s => (
                  <a key={s.l} href={s.href} target="_blank" rel="noopener noreferrer"
                    style={{ display: 'inline-flex', alignItems: 'center', padding: '5px 14px', borderRadius: '6px', background: s.bg, color: '#fff', fontSize: '12px', fontWeight: 700, textDecoration: 'none' }}>
                    {s.l}
                  </a>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

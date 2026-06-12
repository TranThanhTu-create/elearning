import type { Metadata } from 'next'
import { notFound } from 'next/navigation'
import Navbar from '@/components/layout/Navbar'
import Footer from '@/components/layout/Footer'
import CourseBuyBox from './_components/CourseBuyBox'
import CourseAccordion from './_components/CourseAccordion'
import { formatNumber, formatDuration } from '@/lib/utils'
import type { Course } from '@/types'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || 'https://tumarketing.vn'

type Props = { params: Promise<{ slug: string }> }

async function getCourse(slug: string): Promise<Course | null> {
  try {
    const res = await fetch(`${API_URL}/api/courses/${slug}`, { next: { revalidate: 60 } })
    if (!res.ok) return null
    return res.json()
  } catch {
    return null
  }
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params
  const course = await getCourse(slug)
  if (!course) return { title: 'Không tìm thấy khóa học' }

  const description = course.short_desc || course.description?.slice(0, 160) || ''
  const ogImage = course.thumbnail_url
    ? [{ url: course.thumbnail_url, width: 1200, height: 630, alt: course.title }]
    : []

  return {
    title: course.title,
    description,
    openGraph: {
      title: course.title, description,
      url: `${SITE_URL}/courses/${course.slug}`,
      type: 'website', images: ogImage,
    },
    twitter: {
      card: 'summary_large_image', title: course.title, description,
      images: course.thumbnail_url ? [course.thumbnail_url] : [],
    },
    alternates: { canonical: `${SITE_URL}/courses/${course.slug}` },
  }
}

function levelLabel(level: string) {
  return { beginner: 'Cơ bản', intermediate: 'Trung cấp', advanced: 'Nâng cao' }[level] ?? level
}

export default async function CourseDetailPage({ params }: Props) {
  const { slug } = await params
  const course = await getCourse(slug)
  if (!course) notFound()

  const totalDuration = course.chapters
    ?.flatMap(c => c.lessons || [])
    .reduce((s, l) => s + (l.duration_seconds || 0), 0) || 0
  const totalLessons = course.chapters
    ?.flatMap(c => c.lessons || []).length || course.total_lessons || 0
  const freeLessons = course.chapters
    ?.flatMap(c => c.lessons || [])
    .filter(l => l.is_free || l.is_preview).length || 0

  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'Course',
    name: course.title,
    description: course.short_desc || course.description || '',
    url: `${SITE_URL}/courses/${course.slug}`,
    image: course.thumbnail_url || '',
    provider: { '@type': 'Organization', name: 'Tú Marketing', sameAs: SITE_URL },
    ...(course.instructor_name && {
      instructor: { '@type': 'Person', name: course.instructor_name },
    }),
    offers: {
      '@type': 'Offer', price: course.price, priceCurrency: 'VND',
      availability: 'https://schema.org/InStock',
      url: `${SITE_URL}/courses/${course.slug}`,
    },
    aggregateRating: course.reviews_count && course.reviews_count > 0 ? {
      '@type': 'AggregateRating',
      ratingValue: (course.avg_rating ?? 0).toFixed(1),
      reviewCount: course.reviews_count,
      bestRating: '5', worstRating: '1',
    } : undefined,
  }

  const hasOutcomes = course.outcomes && course.outcomes.length > 0
  const hasRequirements = course.requirements && course.requirements.length > 0
  const hasFaq = course.faq && course.faq.length > 0

  return (
    <>
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }} />
      <Navbar />
      <main>

        {/* ── Hero banner ─────────────────────────────── */}
        <div style={{
          background: 'linear-gradient(135deg, #0a0a0f 0%, #0d1117 50%, #0a0a14 100%)',
          borderBottom: '1px solid var(--border)',
          position: 'relative', overflow: 'hidden',
          padding: '56px 0 48px',
        }}>
          {/* Grid overlay */}
          <div style={{ position: 'absolute', inset: 0, backgroundImage: 'linear-gradient(rgba(0,212,255,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(0,212,255,0.03) 1px, transparent 1px)', backgroundSize: '60px 60px', pointerEvents: 'none' }} />
          {/* Glow */}
          <div style={{ position: 'absolute', top: '-80px', left: '30%', width: '500px', height: '300px', background: 'radial-gradient(ellipse, rgba(0,212,255,0.08) 0%, transparent 70%)', pointerEvents: 'none' }} />

          <div className="container" style={{ position: 'relative' }}>
            <div style={{ maxWidth: '720px' }}>
              {/* Category badge */}
              {course.category && (
                <div style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', background: 'rgba(0,212,255,0.08)', border: '1px solid rgba(0,212,255,0.2)', borderRadius: '6px', padding: '4px 12px', fontSize: '12px', color: 'var(--neon)', marginBottom: '14px', fontWeight: 700, letterSpacing: '0.5px', textTransform: 'uppercase' }}>
                  {typeof course.category === 'string' ? course.category : (course.category as {name:string}).name}
                </div>
              )}

              {/* Title */}
              <h1 style={{ fontSize: 'clamp(24px, 3.8vw, 40px)', fontWeight: 900, lineHeight: 1.2, color: 'var(--text)', marginBottom: '14px', letterSpacing: '-0.5px' }}>
                {course.title}
              </h1>

              {/* Subtitle */}
              {(course.subtitle || course.short_desc) && (
                <p style={{ fontSize: '17px', color: 'var(--text-muted)', lineHeight: 1.65, marginBottom: '20px', maxWidth: '640px' }}>
                  {course.subtitle || course.short_desc}
                </p>
              )}

              {/* Stats row */}
              <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap', fontSize: '14px', color: 'var(--text-muted)', marginBottom: '16px' }}>
                {course.avg_rating > 0 && (
                  <span style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                    <span style={{ color: '#f59e0b' }}>★</span>
                    <strong style={{ color: 'var(--text)' }}>{(course.avg_rating).toFixed(1)}</strong>
                    {course.reviews_count ? <span>({formatNumber(course.reviews_count)} đánh giá)</span> : null}
                  </span>
                )}
                <span>👥 <strong style={{ color: 'var(--text)' }}>{formatNumber(course.total_students || course.students_count || 0)}</strong> học viên</span>
                {totalLessons > 0 && <span>📹 {totalLessons} bài học</span>}
                {totalDuration > 0 && <span>⏱ {formatDuration(totalDuration)}</span>}
                {course.level && <span>📊 {levelLabel(course.level)}</span>}
                {course.last_updated && <span>🔄 Cập nhật {course.last_updated}</span>}
              </div>

              {/* Instructor */}
              {course.instructor_name && (
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '14px', color: 'var(--text-muted)' }}>
                  <span style={{ width: '32px', height: '32px', borderRadius: '50%', background: 'rgba(0,212,255,0.12)', border: '1px solid rgba(0,212,255,0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '15px' }}>👨‍🏫</span>
                  <span>Giảng viên: <strong style={{ color: 'var(--text)' }}>{course.instructor_name}</strong></span>
                </div>
              )}

              {/* Free preview badge */}
              {freeLessons > 0 && (
                <div style={{ marginTop: '14px', display: 'inline-flex', alignItems: 'center', gap: '6px', background: 'rgba(0,255,136,0.06)', border: '1px solid rgba(0,255,136,0.2)', borderRadius: '6px', padding: '5px 12px', fontSize: '13px', color: '#00ff88' }}>
                  ▶ {freeLessons} bài học miễn phí — xem trước ngay bên dưới
                </div>
              )}
            </div>
          </div>
        </div>

        {/* ── Body ─────────────────────────────────────── */}
        <div className="section-sm">
          <div className="container">
            <div className="layout-sidebar">

              {/* ── Left column ── */}
              <div style={{ minWidth: 0 }}>

                {/* Trailer video */}
                {course.trailer_video_id && (
                  <div style={{ marginBottom: '24px' }}>
                    <div style={{ position: 'relative', paddingBottom: '56.25%', borderRadius: '14px', overflow: 'hidden', boxShadow: '0 0 40px rgba(0,212,255,0.12)' }}>
                      <iframe
                        src={`https://www.youtube.com/embed/${course.trailer_video_id}?rel=0`}
                        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                        allowFullScreen
                        style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', border: 'none' }}
                      />
                    </div>
                  </div>
                )}

                {/* What you'll learn */}
                {hasOutcomes && (
                  <div style={{ background: 'rgba(0,212,255,0.04)', border: '1px solid rgba(0,212,255,0.15)', borderRadius: '14px', padding: '24px', marginBottom: '20px' }}>
                    <h2 style={{ fontSize: '18px', fontWeight: 800, color: 'var(--text)', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span style={{ width: '28px', height: '28px', background: 'rgba(0,212,255,0.12)', borderRadius: '8px', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', fontSize: '14px' }}>🎯</span>
                      Bạn sẽ học được gì?
                    </h2>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '10px' }}>
                      {course.outcomes!.map((item, i) => (
                        <div key={i} style={{ display: 'flex', gap: '10px', fontSize: '14px', color: 'var(--text-muted)', alignItems: 'flex-start', lineHeight: 1.5 }}>
                          <span style={{ color: '#00ff88', flexShrink: 0, fontWeight: 700, marginTop: '1px' }}>✓</span>
                          <span>{item}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Description */}
                {course.description && (
                  <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: '14px', padding: '24px', marginBottom: '20px' }}>
                    <h2 style={{ fontSize: '18px', fontWeight: 800, color: 'var(--text)', marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span style={{ width: '28px', height: '28px', background: 'rgba(0,212,255,0.12)', borderRadius: '8px', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', fontSize: '14px' }}>📄</span>
                      Mô tả khóa học
                    </h2>
                    <div style={{ fontSize: '15px', lineHeight: 1.8, color: 'var(--text-muted)' }}
                      dangerouslySetInnerHTML={{ __html: course.description.replace(/\n/g, '<br/>') }} />
                  </div>
                )}

                {/* Curriculum */}
                {course.chapters && course.chapters.length > 0 && (
                  <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: '14px', padding: '24px', marginBottom: '20px' }}>
                    <h2 style={{ fontSize: '18px', fontWeight: 800, color: 'var(--text)', marginBottom: '4px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span style={{ width: '28px', height: '28px', background: 'rgba(0,212,255,0.12)', borderRadius: '8px', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', fontSize: '14px' }}>📚</span>
                      Nội dung khóa học
                    </h2>
                    <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginBottom: '16px', marginLeft: '36px' }}>
                      {course.chapters.length} chương · {totalLessons} bài học
                      {totalDuration > 0 && ` · ${formatDuration(totalDuration)}`}
                      {freeLessons > 0 && (
                        <span style={{ marginLeft: '10px', color: '#00ff88', fontWeight: 600 }}>· {freeLessons} bài xem miễn phí</span>
                      )}
                    </p>
                    <CourseAccordion chapters={course.chapters} />
                  </div>
                )}

                {/* Requirements */}
                {hasRequirements && (
                  <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: '14px', padding: '24px', marginBottom: '20px' }}>
                    <h2 style={{ fontSize: '18px', fontWeight: 800, color: 'var(--text)', marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span style={{ width: '28px', height: '28px', background: 'rgba(0,212,255,0.12)', borderRadius: '8px', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', fontSize: '14px' }}>📋</span>
                      Yêu cầu đầu vào
                    </h2>
                    <ul style={{ margin: 0, padding: '0 0 0 4px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                      {course.requirements!.map((req, i) => (
                        <li key={i} style={{ display: 'flex', gap: '10px', fontSize: '14px', color: 'var(--text-muted)', alignItems: 'flex-start', listStyle: 'none' }}>
                          <span style={{ color: 'var(--neon)', flexShrink: 0, marginTop: '2px' }}>›</span>
                          <span>{req}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* FAQ */}
                {hasFaq && (
                  <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: '14px', padding: '24px', marginBottom: '20px' }}>
                    <h2 style={{ fontSize: '18px', fontWeight: 800, color: 'var(--text)', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span style={{ width: '28px', height: '28px', background: 'rgba(0,212,255,0.12)', borderRadius: '8px', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', fontSize: '14px' }}>❓</span>
                      Câu hỏi thường gặp
                    </h2>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                      {course.faq!.map((item, i) => (
                        <div key={i} style={{ background: 'rgba(0,212,255,0.03)', border: '1px solid var(--border)', borderRadius: '10px', padding: '14px 16px' }}>
                          <p style={{ fontWeight: 700, color: 'var(--text)', fontSize: '14px', marginBottom: '6px' }}>Q: {item.q}</p>
                          <p style={{ color: 'var(--text-muted)', fontSize: '14px', lineHeight: 1.6 }}>A: {item.a}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

              </div>

              {/* ── Right: Buy box ── */}
              <CourseBuyBox course={course} totalLessons={totalLessons} totalDuration={totalDuration} />

            </div>
          </div>
        </div>

      </main>
      <Footer />
    </>
  )
}

import type { Metadata } from 'next'
import { notFound } from 'next/navigation'
import Link from 'next/link'
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
    const res = await fetch(`${API_URL}/api/courses/${slug}`, {
      next: { revalidate: 60 },
    })
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
      title: course.title,
      description,
      url: `${SITE_URL}/courses/${course.slug}`,
      type: 'website',
      images: ogImage,
    },
    twitter: {
      card: 'summary_large_image',
      title: course.title,
      description,
      images: course.thumbnail_url ? [course.thumbnail_url] : [],
    },
    alternates: {
      canonical: `${SITE_URL}/courses/${course.slug}`,
    },
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
  const defaultOpenId = course.chapters?.[0]?.id ?? null

  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'Course',
    name: course.title,
    description: course.short_desc || course.description || '',
    url: `${SITE_URL}/courses/${course.slug}`,
    image: course.thumbnail_url || '',
    provider: {
      '@type': 'Organization',
      name: 'Tú Marketing',
      sameAs: SITE_URL,
    },
    ...(course.instructor_name && {
      instructor: { '@type': 'Person', name: course.instructor_name },
    }),
    offers: {
      '@type': 'Offer',
      price: course.price,
      priceCurrency: 'VND',
      availability: 'https://schema.org/InStock',
      url: `${SITE_URL}/courses/${course.slug}`,
    },
    aggregateRating: course.reviews_count && course.reviews_count > 0 ? {
      '@type': 'AggregateRating',
      ratingValue: (course.avg_rating ?? 0).toFixed(1),
      reviewCount: course.reviews_count,
      bestRating: '5',
      worstRating: '1',
    } : undefined,
  }

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <Navbar />
      <main>
        {/* Hero */}
        <div style={{
          background: 'radial-gradient(ellipse 90% 60% at 50% 0%, rgba(0,212,255,0.10) 0%, transparent 65%), var(--bg)',
          borderBottom: '1px solid var(--border)', padding: '48px 0',
          position: 'relative', overflow: 'hidden',
        }}>
          <div style={{ position: 'absolute', inset: 0, backgroundImage: 'linear-gradient(rgba(0,212,255,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(0,212,255,0.03) 1px, transparent 1px)', backgroundSize: '60px 60px', pointerEvents: 'none' }} />
          <div className="container" style={{ position: 'relative' }}>
            <div style={{ maxWidth: '680px' }}>
              {course.category && (
                <div style={{ display: 'inline-block', background: 'rgba(0,212,255,0.08)', border: '1px solid rgba(0,212,255,0.2)', borderRadius: '6px', padding: '3px 10px', fontSize: '12px', color: 'var(--neon)', marginBottom: '12px', fontWeight: 600 }}>
                  {course.category.name}
                </div>
              )}
              <h1 style={{ fontSize: 'clamp(22px, 3.5vw, 34px)', fontWeight: 900, lineHeight: 1.25, color: 'var(--text)', marginBottom: '12px', letterSpacing: '-0.5px' }}>
                {course.title}
              </h1>
              {course.short_desc && (
                <p style={{ fontSize: '16px', color: 'var(--text-muted)', lineHeight: 1.65 }}>{course.short_desc}</p>
              )}
              <div style={{ display: 'flex', gap: '20px', marginTop: '16px', flexWrap: 'wrap', fontSize: '14px', color: 'var(--text-muted)' }}>
                <span>⭐ <strong style={{ color: 'var(--text)' }}>{(course.avg_rating ?? 0).toFixed(1)}</strong> ({formatNumber(course.reviews_count || 0)} đánh giá)</span>
                <span>👥 <strong style={{ color: 'var(--text)' }}>{formatNumber(course.total_students)}</strong> học viên</span>
                {course.level && <span>📊 {levelLabel(course.level)}</span>}
                {course.instructor_name && <span>👨‍🏫 {course.instructor_name}</span>}
              </div>
            </div>
          </div>
        </div>

        {/* Body */}
        <div className="section-sm">
          <div className="container">
            <div className="layout-sidebar">
              {/* Left */}
              <div>
                {/* Description */}
                {course.description && (
                  <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: '14px', padding: '24px', marginBottom: '20px' }}>
                    <h2 style={{ fontSize: '18px', fontWeight: 700, color: 'var(--text)', marginBottom: '12px' }}>Mô tả khóa học</h2>
                    <div style={{ fontSize: '15px', lineHeight: 1.8, color: 'var(--text-muted)' }}
                      dangerouslySetInnerHTML={{ __html: course.description.replace(/\n/g, '<br/>') }} />
                  </div>
                )}

                {/* What you'll learn */}
                <div style={{ background: 'rgba(0,212,255,0.04)', border: '1px solid rgba(0,212,255,0.12)', borderRadius: '14px', padding: '24px', marginBottom: '20px' }}>
                  <h2 style={{ fontSize: '18px', fontWeight: 700, color: 'var(--text)', marginBottom: '16px' }}>Bạn sẽ học được gì?</h2>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '8px' }}>
                    {[
                      'Xây dựng AI Agent từ zero',
                      'Tự động hóa Marketing 24/7',
                      'Tích hợp Zalo & Facebook',
                      'Scale doanh nghiệp với AI',
                      'Không cần biết code',
                      'Triển khai thực tế ngay',
                    ].map(item => (
                      <div key={item} style={{ display: 'flex', gap: '8px', fontSize: '14px', color: 'var(--text-muted)', alignItems: 'flex-start' }}>
                        <span style={{ color: 'var(--neon-green)', flexShrink: 0, marginTop: '1px' }}>✓</span>
                        <span>{item}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Curriculum */}
                {course.chapters && course.chapters.length > 0 && (
                  <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: '14px', padding: '24px' }}>
                    <h2 style={{ fontSize: '18px', fontWeight: 700, color: 'var(--text)', marginBottom: '4px' }}>Nội dung khóa học</h2>
                    <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginBottom: '16px' }}>
                      {course.chapters.length} chương · {totalLessons} bài học · {formatDuration(totalDuration)}
                    </p>
                    <CourseAccordion chapters={course.chapters} defaultOpenId={defaultOpenId} />
                  </div>
                )}
              </div>

              {/* Right: Buy box (Client Component) */}
              <CourseBuyBox course={course} totalLessons={totalLessons} totalDuration={totalDuration} />
            </div>
          </div>
        </div>
      </main>
      <Footer />
    </>
  )
}

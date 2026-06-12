import type { Metadata } from 'next'
import { notFound } from 'next/navigation'
import Navbar from '@/components/layout/Navbar'
import Footer from '@/components/layout/Footer'
import CourseBuyBox from './_components/CourseBuyBox'
import CourseBuyHeroBtn from './_components/CourseBuyHeroBtn'
import CourseAccordion from './_components/CourseAccordion'
import StickyBuyBar from './_components/StickyBuyBar'
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
    openGraph: { title: course.title, description, url: `${SITE_URL}/courses/${course.slug}`, type: 'website', images: ogImage },
    twitter: { card: 'summary_large_image', title: course.title, description, images: course.thumbnail_url ? [course.thumbnail_url] : [] },
    alternates: { canonical: `${SITE_URL}/courses/${course.slug}` },
  }
}

function levelLabel(l: string) {
  return { beginner: 'Cơ bản', intermediate: 'Trung cấp', advanced: 'Nâng cao' }[l] ?? l
}

function StarRating({ rating }: { rating: number }) {
  return (
    <span style={{ color: '#f59e0b', fontSize: '16px', letterSpacing: '1px' }}>
      {'★'.repeat(Math.round(rating))}{'☆'.repeat(5 - Math.round(rating))}
    </span>
  )
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

  const hasOutcomes = (course.outcomes?.length || 0) > 0
  const hasRequirements = (course.requirements?.length || 0) > 0
  const hasFaq = (course.faq?.length || 0) > 0
  const hasChapters = (course.chapters?.length || 0) > 0

  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'Course',
    name: course.title,
    description: course.short_desc || course.description || '',
    url: `${SITE_URL}/courses/${course.slug}`,
    image: course.thumbnail_url || '',
    provider: { '@type': 'Organization', name: 'Tú Marketing', sameAs: SITE_URL },
    ...(course.instructor_name && { instructor: { '@type': 'Person', name: course.instructor_name } }),
    offers: { '@type': 'Offer', price: course.price, priceCurrency: 'VND', availability: 'https://schema.org/InStock', url: `${SITE_URL}/courses/${course.slug}` },
    aggregateRating: course.reviews_count && course.reviews_count > 0 ? {
      '@type': 'AggregateRating',
      ratingValue: (course.avg_rating ?? 0).toFixed(1),
      reviewCount: course.reviews_count,
      bestRating: '5', worstRating: '1',
    } : undefined,
  }

  /* ── INLINE STYLES shortcuts ── */
  const S = {
    section: (bg?: string): React.CSSProperties => ({
      padding: '64px 0',
      background: bg || 'transparent',
    }),
    wrap: (): React.CSSProperties => ({
      maxWidth: '860px', margin: '0 auto', padding: '0 24px',
    }),
    sectionTitle: (): React.CSSProperties => ({
      fontSize: 'clamp(22px, 3vw, 30px)', fontWeight: 900, color: 'var(--text)',
      marginBottom: '8px', letterSpacing: '-0.3px',
    }),
    sectionSub: (): React.CSSProperties => ({
      fontSize: '15px', color: 'var(--text-muted)', marginBottom: '28px',
    }),
    divider: (): React.CSSProperties => ({
      width: '48px', height: '3px', borderRadius: '2px',
      background: 'linear-gradient(90deg, var(--neon), var(--neon-purple))',
      marginBottom: '16px',
    }),
  }

  return (
    <>
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }} />

      {/* Sticky buy bar (client) */}
      <StickyBuyBar course={course} />

      <Navbar />

      <main>
        {/* ══════════════════════════════════════════
            SECTION 1: HERO
        ══════════════════════════════════════════ */}
        <section style={{
          background: 'linear-gradient(160deg, #070b14 0%, #0c1428 60%, #070b14 100%)',
          borderBottom: '1px solid var(--border)',
          position: 'relative', overflow: 'hidden',
          padding: '72px 0 60px',
        }}>
          {/* Grid lines */}
          <div style={{ position: 'absolute', inset: 0, backgroundImage: 'linear-gradient(rgba(0,212,255,0.04) 1px, transparent 1px), linear-gradient(90deg, rgba(0,212,255,0.04) 1px, transparent 1px)', backgroundSize: '60px 60px', pointerEvents: 'none' }} />
          {/* Glow orbs */}
          <div style={{ position: 'absolute', top: '-100px', right: '10%', width: '600px', height: '400px', background: 'radial-gradient(ellipse, rgba(0,212,255,0.07) 0%, transparent 65%)', pointerEvents: 'none' }} />
          <div style={{ position: 'absolute', bottom: '-60px', left: '5%', width: '400px', height: '300px', background: 'radial-gradient(ellipse, rgba(123,47,255,0.06) 0%, transparent 65%)', pointerEvents: 'none' }} />

          <div style={S.wrap()}>
            {/* Category badge */}
            {course.category && (
              <div style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', background: 'rgba(0,212,255,0.08)', border: '1px solid rgba(0,212,255,0.25)', borderRadius: '20px', padding: '4px 14px', fontSize: '12px', color: 'var(--neon)', marginBottom: '20px', fontWeight: 700, letterSpacing: '0.8px', textTransform: 'uppercase' }}>
                {typeof course.category === 'string' ? course.category : (course.category as {name:string}).name}
              </div>
            )}

            {/* Title */}
            <h1 style={{ fontSize: 'clamp(28px, 5vw, 52px)', fontWeight: 900, lineHeight: 1.15, color: 'var(--text)', marginBottom: '16px', letterSpacing: '-1px', maxWidth: '780px' }}>
              {course.title}
            </h1>

            {/* Subtitle */}
            {(course.subtitle || course.short_desc) && (
              <p style={{ fontSize: 'clamp(15px, 2vw, 18px)', color: 'var(--text-muted)', lineHeight: 1.7, marginBottom: '24px', maxWidth: '680px' }}>
                {course.subtitle || course.short_desc}
              </p>
            )}

            {/* Stats */}
            <div style={{ display: 'flex', gap: '24px', flexWrap: 'wrap', fontSize: '14px', color: 'var(--text-muted)', marginBottom: '28px', alignItems: 'center' }}>
              {course.avg_rating > 0 && (
                <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <StarRating rating={course.avg_rating} />
                  <strong style={{ color: 'var(--text)' }}>{course.avg_rating.toFixed(1)}</strong>
                  {course.reviews_count ? <span>({formatNumber(course.reviews_count)} đánh giá)</span> : null}
                </span>
              )}
              <span>👥 <strong style={{ color: 'var(--text)' }}>{formatNumber(course.total_students || course.students_count || 0)}</strong> học viên</span>
              {totalLessons > 0 && <span>📹 {totalLessons} bài học</span>}
              {totalDuration > 0 && <span>⏱ {formatDuration(totalDuration)}</span>}
              {course.level && <span>📊 {levelLabel(course.level)}</span>}
              {course.last_updated && <span style={{ color: 'var(--text-dim)' }}>🔄 Cập nhật {course.last_updated}</span>}
            </div>

            {/* Instructor row */}
            {course.instructor_name && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '28px' }}>
                <div style={{ width: '40px', height: '40px', borderRadius: '50%', background: 'linear-gradient(135deg, var(--neon), var(--neon-purple))', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '18px', flexShrink: 0 }}>
                  👨‍🏫
                </div>
                <div>
                  <div style={{ fontSize: '12px', color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Giảng viên</div>
                  <div style={{ fontSize: '15px', fontWeight: 700, color: 'var(--text)' }}>{course.instructor_name}</div>
                </div>
              </div>
            )}

            {/* CTA buttons */}
            <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', alignItems: 'center' }}>
              <CourseBuyHeroBtn course={course} />
              {freeLessons > 0 && (
                <a href="#curriculum" style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', padding: '13px 24px', borderRadius: 'var(--radius-lg)', border: '1.5px solid var(--border-bright)', color: 'var(--text)', fontSize: '15px', fontWeight: 600, textDecoration: 'none', transition: 'border-color 0.2s' }}>
                  ▶ Xem {freeLessons} bài học miễn phí
                </a>
              )}
            </div>
          </div>
        </section>

        {/* ══════════════════════════════════════════
            SECTION 2: QUICK STATS BAR
        ══════════════════════════════════════════ */}
        <div style={{ background: 'var(--bg-elevated)', borderBottom: '1px solid var(--border)', padding: '16px 0' }}>
          <div style={S.wrap()}>
            <div style={{ display: 'flex', gap: '0', flexWrap: 'wrap', justifyContent: 'space-around' }}>
              {[
                { v: formatNumber(course.total_students || 0) + '+', l: 'Học viên' },
                { v: totalLessons + '', l: 'Bài học' },
                ...(totalDuration > 0 ? [{ v: formatDuration(totalDuration), l: 'Video' }] : []),
                { v: '♾️', l: 'Trọn đời' },
                { v: '🏆', l: 'Chứng chỉ' },
              ].map(({ v, l }) => (
                <div key={l} style={{ textAlign: 'center', padding: '8px 16px' }}>
                  <div style={{ fontSize: '18px', fontWeight: 900, color: 'var(--neon)' }}>{v}</div>
                  <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '2px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>{l}</div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* ══════════════════════════════════════════
            SECTION 3: WHAT YOU'LL LEARN
        ══════════════════════════════════════════ */}
        {hasOutcomes && (
          <section style={S.section()}>
            <div style={S.wrap()}>
              <div style={S.divider()} />
              <h2 style={S.sectionTitle()}>Bạn sẽ học được gì?</h2>
              <p style={S.sectionSub()}>Những kỹ năng và kiến thức bạn sẽ nắm vững sau khi hoàn thành khóa học</p>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '12px' }}>
                {course.outcomes!.map((item, i) => (
                  <div key={i} style={{
                    display: 'flex', gap: '12px', padding: '14px 16px',
                    background: 'var(--bg-card)', borderRadius: '10px',
                    border: '1px solid var(--border)', fontSize: '14px',
                    color: 'var(--text-muted)', alignItems: 'flex-start',
                    lineHeight: 1.5, transition: 'border-color 0.2s',
                  }}>
                    <span style={{ color: '#00ff88', fontWeight: 900, fontSize: '16px', flexShrink: 0, marginTop: '1px' }}>✓</span>
                    <span>{item}</span>
                  </div>
                ))}
              </div>
            </div>
          </section>
        )}

        {/* ══════════════════════════════════════════
            SECTION 4: TRAILER VIDEO
        ══════════════════════════════════════════ */}
        {course.trailer_video_id && (
          <section style={S.section('rgba(0,212,255,0.02)')}>
            <div style={S.wrap()}>
              <div style={{ textAlign: 'center', marginBottom: '24px' }}>
                <div style={S.divider()} />
                <h2 style={S.sectionTitle()}>Xem trước nội dung khóa học</h2>
                <p style={S.sectionSub()}>Video giới thiệu — hoàn toàn miễn phí</p>
              </div>
              <div style={{ position: 'relative', paddingBottom: '56.25%', borderRadius: '14px', overflow: 'hidden', boxShadow: '0 0 60px rgba(0,212,255,0.15)' }}>
                <iframe
                  src={`https://www.youtube.com/embed/${course.trailer_video_id}?rel=0`}
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowFullScreen
                  style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', border: 'none' }}
                />
              </div>
            </div>
          </section>
        )}

        {/* ══════════════════════════════════════════
            SECTION 5: DESCRIPTION
        ══════════════════════════════════════════ */}
        {course.description && (
          <section style={S.section()}>
            <div style={S.wrap()}>
              <div style={S.divider()} />
              <h2 style={S.sectionTitle()}>Về khóa học này</h2>
              <div style={{ fontSize: '15px', lineHeight: 1.85, color: 'var(--text-muted)' }}
                dangerouslySetInnerHTML={{ __html: course.description.replace(/\n/g, '<br/>') }} />
            </div>
          </section>
        )}

        {/* ══════════════════════════════════════════
            SECTION 6: CURRICULUM
        ══════════════════════════════════════════ */}
        {hasChapters && (
          <section id="curriculum" style={S.section('var(--bg-elevated)')}>
            <div style={S.wrap()}>
              <div style={S.divider()} />
              <h2 style={S.sectionTitle()}>Nội dung khóa học</h2>
              <p style={S.sectionSub()}>
                {course.chapters!.length} chương · {totalLessons} bài học
                {totalDuration > 0 && ` · ${formatDuration(totalDuration)}`}
                {freeLessons > 0 && <span style={{ color: '#00ff88', marginLeft: '10px', fontWeight: 700 }}>· {freeLessons} bài xem miễn phí</span>}
              </p>
              <CourseAccordion chapters={course.chapters!} />
            </div>
          </section>
        )}

        {/* ══════════════════════════════════════════
            SECTION 7: INSTRUCTOR
        ══════════════════════════════════════════ */}
        {course.instructor_name && (
          <section style={S.section()}>
            <div style={S.wrap()}>
              <div style={S.divider()} />
              <h2 style={S.sectionTitle()}>Giảng viên</h2>
              <p style={S.sectionSub()}>Người trực tiếp hướng dẫn bạn trong suốt khóa học</p>
              <div style={{
                display: 'flex', gap: '24px', alignItems: 'flex-start',
                background: 'var(--bg-card)', border: '1px solid var(--border-bright)',
                borderRadius: '16px', padding: '28px',
                boxShadow: '0 4px 24px rgba(0,212,255,0.06)',
              }}>
                <div style={{ width: '80px', height: '80px', borderRadius: '50%', background: 'linear-gradient(135deg, #00d4ff 0%, #7b2fff 100%)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '36px', flexShrink: 0 }}>
                  👨‍🏫
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: '20px', fontWeight: 800, color: 'var(--text)', marginBottom: '6px' }}>{course.instructor_name}</div>
                  <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap', fontSize: '13px', color: 'var(--text-muted)', marginBottom: '12px' }}>
                    <span>⭐ {(course.avg_rating || 0).toFixed(1)} điểm đánh giá</span>
                    <span>👥 {formatNumber(course.total_students || 0)} học viên</span>
                    <span>📹 {totalLessons} bài học</span>
                  </div>
                  {course.short_desc && (
                    <p style={{ fontSize: '14px', color: 'var(--text-muted)', lineHeight: 1.7 }}>
                      Chuyên gia với nhiều năm kinh nghiệm thực chiến. Giảng viên trực tiếp dẫn dắt học viên qua từng bước một cách rõ ràng và thực tế.
                    </p>
                  )}
                </div>
              </div>
            </div>
          </section>
        )}

        {/* ══════════════════════════════════════════
            SECTION 8: REQUIREMENTS
        ══════════════════════════════════════════ */}
        {hasRequirements && (
          <section style={S.section('rgba(123,47,255,0.03)')}>
            <div style={S.wrap()}>
              <div style={S.divider()} />
              <h2 style={S.sectionTitle()}>Yêu cầu đầu vào</h2>
              <p style={S.sectionSub()}>Bạn cần chuẩn bị những điều sau trước khi bắt đầu</p>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {course.requirements!.map((req, i) => (
                  <div key={i} style={{ display: 'flex', gap: '12px', fontSize: '14px', color: 'var(--text-muted)', alignItems: 'flex-start', padding: '12px 16px', background: 'var(--bg-card)', borderRadius: '10px', border: '1px solid var(--border)' }}>
                    <span style={{ color: 'var(--neon)', fontWeight: 700, fontSize: '16px', flexShrink: 0, marginTop: '1px' }}>›</span>
                    <span style={{ lineHeight: 1.6 }}>{req}</span>
                  </div>
                ))}
              </div>
            </div>
          </section>
        )}

        {/* ══════════════════════════════════════════
            SECTION 9: FAQ
        ══════════════════════════════════════════ */}
        {hasFaq && (
          <section style={S.section()}>
            <div style={S.wrap()}>
              <div style={S.divider()} />
              <h2 style={S.sectionTitle()}>Câu hỏi thường gặp</h2>
              <p style={S.sectionSub()}>Những thắc mắc phổ biến từ học viên</p>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {course.faq!.map((item, i) => (
                  <details key={i} style={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: '12px', overflow: 'hidden', cursor: 'pointer' }}>
                    <summary style={{ padding: '16px 20px', fontWeight: 700, fontSize: '15px', color: 'var(--text)', listStyle: 'none', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      {item.q}
                      <span style={{ color: 'var(--neon)', fontSize: '18px', flexShrink: 0, marginLeft: '12px' }}>+</span>
                    </summary>
                    <div style={{ padding: '0 20px 16px', fontSize: '14px', color: 'var(--text-muted)', lineHeight: 1.7, borderTop: '1px solid var(--border)' }}>
                      <div style={{ paddingTop: '12px' }}>{item.a}</div>
                    </div>
                  </details>
                ))}
              </div>
            </div>
          </section>
        )}

        {/* ══════════════════════════════════════════
            SECTION 10: FINAL PRICING CTA
        ══════════════════════════════════════════ */}
        <CourseBuyBox course={course} totalLessons={totalLessons} totalDuration={totalDuration} />

      </main>
      <Footer />
    </>
  )
}

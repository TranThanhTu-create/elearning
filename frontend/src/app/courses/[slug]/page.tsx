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

/* ─────────────────────────────────────────
   Shared style helpers
───────────────────────────────────────── */
const maxW: React.CSSProperties = { maxWidth: '900px', margin: '0 auto', padding: '0 24px' }
const divider = (
  <div style={{ width: '48px', height: '3px', background: 'linear-gradient(90deg,#00d4ff,#7b2fff)', borderRadius: '2px', marginBottom: '16px' }} />
)

function SectionHeader({ tag, title, sub }: { tag?: string; title: string; sub?: string }) {
  return (
    <div style={{ marginBottom: '32px' }}>
      {tag && (
        <div style={{ display: 'inline-block', background: 'rgba(0,212,255,0.08)', border: '1px solid rgba(0,212,255,0.2)', borderRadius: '20px', padding: '3px 14px', fontSize: '11px', color: 'var(--neon)', fontWeight: 800, letterSpacing: '1px', textTransform: 'uppercase', marginBottom: '14px' }}>
          {tag}
        </div>
      )}
      {divider}
      <h2 style={{ fontSize: 'clamp(22px, 3vw, 32px)', fontWeight: 900, color: 'var(--text)', letterSpacing: '-0.3px', marginBottom: sub ? '8px' : '0' }}>
        {title}
      </h2>
      {sub && <p style={{ fontSize: '15px', color: 'var(--text-muted)' }}>{sub}</p>}
    </div>
  )
}

export default async function CourseDetailPage({ params }: Props) {
  const { slug } = await params
  const course = await getCourse(slug)
  if (!course) notFound()

  const totalDuration = course.chapters
    ?.flatMap(c => c.lessons || []).reduce((s, l) => s + (l.duration_seconds || 0), 0) || 0
  const totalLessons = course.chapters
    ?.flatMap(c => c.lessons || []).length || course.total_lessons || 0
  const freeLessons = course.chapters
    ?.flatMap(c => c.lessons || []).filter(l => l.is_free || l.is_preview).length || 0

  const hasOutcomes = (course.outcomes?.length || 0) > 0
  const hasRequirements = (course.requirements?.length || 0) > 0
  const hasFaq = (course.faq?.length || 0) > 0
  const hasChapters = (course.chapters?.length || 0) > 0
  const hasDiscount = course.original_price && course.original_price > course.price

  // Derive category name
  const catName = course.category
    ? (typeof course.category === 'string' ? course.category : (course.category as {name:string}).name)
    : null

  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'Course',
    name: course.title,
    description: course.short_desc || course.description || '',
    url: `${SITE_URL}/courses/${course.slug}`,
    image: course.thumbnail_url || '',
    provider: { '@type': 'Organization', name: 'Tú Marketing', sameAs: SITE_URL },
    ...(course.instructor_name && { instructor: { '@type': 'Person', name: course.instructor_name } }),
    offers: { '@type': 'Offer', price: course.price, priceCurrency: 'VND', availability: 'https://schema.org/InStock' },
    aggregateRating: course.reviews_count && course.reviews_count > 0 ? {
      '@type': 'AggregateRating',
      ratingValue: (course.avg_rating ?? 0).toFixed(1),
      reviewCount: course.reviews_count, bestRating: '5', worstRating: '1',
    } : undefined,
  }

  const formatVndServer = (n: number) => n.toLocaleString('vi-VN') + ' ₫'

  return (
    <>
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }} />
      <StickyBuyBar course={course} />
      <Navbar />

      <main>
        {/* ══════════════════════════════════════
            HERO
        ══════════════════════════════════════ */}
        <section style={{
          background: 'linear-gradient(160deg,#070b14 0%,#0c1428 55%,#0a0f1e 100%)',
          borderBottom: '1px solid var(--border)',
          position: 'relative', overflow: 'hidden',
          padding: '80px 0 64px',
        }}>
          {/* BG grid */}
          <div style={{ position: 'absolute', inset: 0, backgroundImage: 'linear-gradient(rgba(0,212,255,0.04) 1px,transparent 1px),linear-gradient(90deg,rgba(0,212,255,0.04) 1px,transparent 1px)', backgroundSize: '60px 60px', pointerEvents: 'none' }} />
          {/* Glow */}
          <div style={{ position: 'absolute', top: '-80px', right: '8%', width: '600px', height: '400px', background: 'radial-gradient(ellipse,rgba(0,212,255,0.08) 0%,transparent 65%)', pointerEvents: 'none' }} />
          <div style={{ position: 'absolute', bottom: '-40px', left: '5%', width: '400px', height: '300px', background: 'radial-gradient(ellipse,rgba(123,47,255,0.06) 0%,transparent 65%)', pointerEvents: 'none' }} />

          <div style={maxW}>
            {catName && (
              <div style={{ display: 'inline-flex', gap: '6px', alignItems: 'center', background: 'rgba(0,212,255,0.08)', border: '1px solid rgba(0,212,255,0.25)', borderRadius: '20px', padding: '4px 14px', fontSize: '11px', color: 'var(--neon)', marginBottom: '20px', fontWeight: 800, letterSpacing: '1px', textTransform: 'uppercase' }}>
                {catName}
              </div>
            )}
            <h1 style={{ fontSize: 'clamp(30px, 5.5vw, 56px)', fontWeight: 900, lineHeight: 1.13, color: 'var(--text)', marginBottom: '18px', letterSpacing: '-1.5px', maxWidth: '800px' }}>
              {course.title}
            </h1>
            {(course.subtitle || course.short_desc) && (
              <p style={{ fontSize: 'clamp(15px, 2vw, 19px)', color: 'var(--text-muted)', lineHeight: 1.7, marginBottom: '24px', maxWidth: '680px' }}>
                {course.subtitle || course.short_desc}
              </p>
            )}

            {/* Social proof row */}
            <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap', fontSize: '14px', color: 'var(--text-muted)', marginBottom: '28px', alignItems: 'center' }}>
              {course.avg_rating > 0 && (
                <span style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                  <span style={{ color: '#f59e0b', fontSize: '16px' }}>{'★'.repeat(Math.min(5, Math.round(course.avg_rating)))}</span>
                  <strong style={{ color: 'var(--text)' }}>{course.avg_rating.toFixed(1)}</strong>
                  {course.reviews_count ? <span>({formatNumber(course.reviews_count)} đánh giá)</span> : null}
                </span>
              )}
              <span>👥 <strong style={{ color: 'var(--text)' }}>{formatNumber(course.total_students || 0)}</strong> học viên</span>
              {totalLessons > 0 && <span>📹 {totalLessons} bài học</span>}
              {totalDuration > 0 && <span>⏱ {formatDuration(totalDuration)}</span>}
              {course.level && <span>📊 {levelLabel(course.level)}</span>}
              {course.last_updated && <span style={{ color: 'var(--text-dim)' }}>🔄 Cập nhật {course.last_updated}</span>}
            </div>

            {/* Instructor */}
            {course.instructor_name && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '28px' }}>
                <div style={{ width: '38px', height: '38px', borderRadius: '50%', background: 'linear-gradient(135deg,#00d4ff,#7b2fff)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '17px', flexShrink: 0 }}>
                  👨‍🏫
                </div>
                <div>
                  <div style={{ fontSize: '11px', color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Giảng viên</div>
                  <div style={{ fontSize: '15px', fontWeight: 700, color: 'var(--text)' }}>{course.instructor_name}</div>
                </div>
              </div>
            )}

            {/* CTA */}
            <CourseBuyHeroBtn course={course} />

            {freeLessons > 0 && (
              <div style={{ marginTop: '16px', display: 'inline-flex', alignItems: 'center', gap: '7px', background: 'rgba(0,255,136,0.06)', border: '1px solid rgba(0,255,136,0.2)', borderRadius: '8px', padding: '7px 14px', fontSize: '13px', color: '#00ff88' }}>
                ▶ {freeLessons} bài học miễn phí — <a href="#curriculum" style={{ color: '#00ff88', textDecoration: 'underline', fontWeight: 700 }}>Xem ngay</a>
              </div>
            )}
          </div>
        </section>

        {/* ══════════════════════════════════════
            STATS BAR
        ══════════════════════════════════════ */}
        <div style={{ background: 'var(--bg-elevated)', borderBottom: '1px solid var(--border)', padding: '0' }}>
          <div style={maxW}>
            <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'space-around' }}>
              {[
                { v: formatNumber(course.total_students || 0) + '+', l: 'Học Viên', icon: '👥' },
                { v: String(totalLessons), l: 'Bài Học', icon: '📹' },
                ...(totalDuration > 0 ? [{ v: formatDuration(totalDuration), l: 'Nội Dung', icon: '⏱' }] : []),
                { v: '♾️', l: 'Trọn Đời', icon: '' },
                { v: '🏆', l: 'Chứng Chỉ', icon: '' },
                { v: '🛡️', l: 'Bảo Hành 7 Ngày', icon: '' },
              ].map(({ v, l }) => (
                <div key={l} style={{ textAlign: 'center', padding: '18px 12px', flex: '1', minWidth: '90px' }}>
                  <div style={{ fontSize: '20px', fontWeight: 900, color: 'var(--neon)', lineHeight: 1 }}>{v}</div>
                  <div style={{ fontSize: '10px', color: 'var(--text-muted)', marginTop: '4px', textTransform: 'uppercase', letterSpacing: '0.6px' }}>{l}</div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* ══════════════════════════════════════
            SECTION: TẠI SAO CẦN HỌC NGAY (Always shown)
        ══════════════════════════════════════ */}
        <section style={{ padding: '72px 0', background: 'var(--bg)' }}>
          <div style={maxW}>
            <SectionHeader
              tag="Tại sao cần học ngay"
              title="Mỗi ngày không học là mỗi ngày bạn tụt hậu"
              sub="Thị trường thay đổi liên tục. Người thành công là người hành động sớm nhất."
            />
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
              {[
                { icon: '🎯', title: 'Kiến thức thực chiến', desc: 'Học xong áp dụng được ngay, không lý thuyết suông' },
                { icon: '⚡', title: 'Tiết kiệm thời gian', desc: 'Không mò mẫm tự học, đi thẳng vào bản chất' },
                { icon: '💰', title: 'ROI rõ ràng', desc: 'Học phí nhỏ, giá trị thu về gấp nhiều lần' },
                { icon: '🤝', title: 'Hỗ trợ tận tâm', desc: 'Hỏi gì cũng được trả lời, không bỏ lại học viên' },
              ].map(c => (
                <div key={c.title} style={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: '14px', padding: '22px', transition: 'border-color 0.2s,box-shadow 0.2s' }}
                  onMouseOver={undefined}>
                  <div style={{ fontSize: '32px', marginBottom: '12px' }}>{c.icon}</div>
                  <div style={{ fontWeight: 700, fontSize: '15px', color: 'var(--text)', marginBottom: '6px' }}>{c.title}</div>
                  <div style={{ fontSize: '13px', color: 'var(--text-muted)', lineHeight: 1.6 }}>{c.desc}</div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ══════════════════════════════════════
            SECTION: OUTCOMES (dynamic)
        ══════════════════════════════════════ */}
        {hasOutcomes && (
          <section style={{ padding: '72px 0', background: 'rgba(0,212,255,0.02)' }}>
            <div style={maxW}>
              <SectionHeader
                tag="Kết quả đạt được"
                title="Bạn sẽ học được gì?"
                sub="Những kỹ năng bạn sẽ nắm vững sau khi hoàn thành"
              />
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '10px' }}>
                {course.outcomes!.map((item, i) => (
                  <div key={i} style={{ display: 'flex', gap: '12px', padding: '14px 16px', background: 'var(--bg-card)', borderRadius: '10px', border: '1px solid var(--border)', fontSize: '14px', color: 'var(--text-muted)', lineHeight: 1.55 }}>
                    <span style={{ color: '#00ff88', fontWeight: 900, fontSize: '15px', flexShrink: 0, marginTop: '1px' }}>✓</span>
                    <span>{item}</span>
                  </div>
                ))}
              </div>
            </div>
          </section>
        )}

        {/* ══════════════════════════════════════
            SECTION: TRAILER (dynamic)
        ══════════════════════════════════════ */}
        {course.trailer_video_id && (
          <section style={{ padding: '72px 0', background: 'var(--bg)' }}>
            <div style={maxW}>
              <SectionHeader tag="Preview" title="Xem trước nội dung khóa học" sub="Video giới thiệu — hoàn toàn miễn phí" />
              <div style={{ position: 'relative', paddingBottom: '56.25%', borderRadius: '14px', overflow: 'hidden', boxShadow: '0 0 60px rgba(0,212,255,0.15)' }}>
                <iframe src={`https://www.youtube.com/embed/${course.trailer_video_id}?rel=0`}
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowFullScreen style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', border: 'none' }} />
              </div>
            </div>
          </section>
        )}

        {/* ══════════════════════════════════════
            SECTION: DESCRIPTION (dynamic)
        ══════════════════════════════════════ */}
        {course.description && (
          <section style={{ padding: '72px 0', background: 'rgba(0,212,255,0.02)' }}>
            <div style={maxW}>
              <SectionHeader tag="Về khóa học" title="Khóa học này dành cho bạn nếu…" />
              <div style={{ fontSize: '15px', lineHeight: 1.9, color: 'var(--text-muted)' }}
                dangerouslySetInnerHTML={{ __html: course.description.replace(/\n/g, '<br/>') }} />
            </div>
          </section>
        )}

        {/* ══════════════════════════════════════
            SECTION: MID-PAGE URGENCY CTA (Always shown)
        ══════════════════════════════════════ */}
        <section style={{ padding: '0', background: 'var(--bg)' }}>
          <div style={maxW}>
            <div style={{
              background: 'linear-gradient(135deg, rgba(0,212,255,0.08) 0%, rgba(123,47,255,0.08) 100%)',
              border: '1px solid rgba(0,212,255,0.2)',
              borderRadius: '16px', padding: '36px',
              display: 'flex', alignItems: 'center', justifyContent: 'space-between',
              flexWrap: 'wrap', gap: '20px',
              marginBottom: '72px',
            }}>
              <div>
                <div style={{ fontSize: '13px', color: 'var(--neon)', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '1px', marginBottom: '8px' }}>
                  🔥 Ưu đãi đặc biệt
                </div>
                <div style={{ fontSize: 'clamp(18px, 2.5vw, 26px)', fontWeight: 900, color: 'var(--text)', marginBottom: '6px' }}>
                  {hasDiscount
                    ? `Tiết kiệm ${course.discount_percent}% — Chỉ còn ${formatVndServer(course.price)}`
                    : course.price === 0
                    ? 'Hoàn toàn miễn phí — Đăng ký ngay hôm nay'
                    : `Chỉ ${formatVndServer(course.price)} — Truy cập trọn đời`}
                </div>
                <div style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
                  🛡️ Đảm bảo hoàn tiền 100% trong 7 ngày nếu không hài lòng
                </div>
              </div>
              <CourseBuyHeroBtn course={course} />
            </div>
          </div>
        </section>

        {/* ══════════════════════════════════════
            SECTION: CURRICULUM (dynamic)
        ══════════════════════════════════════ */}
        {hasChapters && (
          <section id="curriculum" style={{ padding: '72px 0', background: 'var(--bg-elevated)' }}>
            <div style={maxW}>
              <SectionHeader
                tag="Chương trình học"
                title="Nội dung khóa học"
                sub={`${course.chapters!.length} chương · ${totalLessons} bài học${totalDuration > 0 ? ` · ${formatDuration(totalDuration)}` : ''}${freeLessons > 0 ? ` · ${freeLessons} bài xem miễn phí` : ''}`}
              />
              <CourseAccordion chapters={course.chapters!} />
            </div>
          </section>
        )}

        {/* ══════════════════════════════════════
            SECTION: PLATFORM TRUST (Always shown)
        ══════════════════════════════════════ */}
        <section style={{ padding: '72px 0', background: 'var(--bg)' }}>
          <div style={maxW}>
            <SectionHeader
              tag="Cam kết của chúng tôi"
              title="Tại sao chọn Tú Marketing Academy?"
              sub="Chúng tôi không chỉ dạy lý thuyết — chúng tôi đồng hành đến khi bạn có kết quả thực tế"
            />
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '20px' }}>
              {[
                {
                  icon: '🎓', color: '#00d4ff',
                  title: '100% Thực Chiến',
                  desc: 'Mỗi bài học đều có ví dụ thực tế và bài tập áp dụng ngay vào công việc hàng ngày của bạn.',
                },
                {
                  icon: '💬', color: '#7b2fff',
                  title: 'Hỗ Trợ 1-1',
                  desc: 'Đặt câu hỏi bất cứ lúc nào. Giảng viên cam kết trả lời trong vòng 24 giờ cho mọi thắc mắc.',
                },
                {
                  icon: '🔄', color: '#00ff88',
                  title: 'Cập Nhật Liên Tục',
                  desc: 'Nội dung khóa học được cập nhật thường xuyên theo xu hướng mới nhất, bạn trả phí 1 lần xem mãi mãi.',
                },
                {
                  icon: '🏆', color: '#f59e0b',
                  title: 'Chứng Chỉ Hoàn Thành',
                  desc: 'Nhận chứng chỉ sau khi hoàn thành khóa học. Tăng uy tín chuyên môn và thêm vào hồ sơ xin việc.',
                },
                {
                  icon: '🛡️', color: '#ff6b35',
                  title: 'Bảo Hành 7 Ngày',
                  desc: 'Không hài lòng? Hoàn tiền 100% trong 7 ngày đầu tiên, không cần lý do, không hỏi thêm.',
                },
                {
                  icon: '📱', color: '#00d4ff',
                  title: 'Học Mọi Lúc Mọi Nơi',
                  desc: 'Xem trên điện thoại, máy tính, tablet. Học theo tiến độ của bạn, không áp lực thời gian.',
                },
              ].map(c => (
                <div key={c.title} style={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: '16px', padding: '24px', transition: 'border-color 0.2s, transform 0.2s, box-shadow 0.2s' }}>
                  <div style={{ width: '48px', height: '48px', borderRadius: '12px', background: `${c.color}18`, border: `1px solid ${c.color}30`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '22px', marginBottom: '14px' }}>
                    {c.icon}
                  </div>
                  <div style={{ fontWeight: 800, fontSize: '15px', color: 'var(--text)', marginBottom: '8px' }}>{c.title}</div>
                  <div style={{ fontSize: '13px', color: 'var(--text-muted)', lineHeight: 1.65 }}>{c.desc}</div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ══════════════════════════════════════
            SECTION: INSTRUCTOR (dynamic)
        ══════════════════════════════════════ */}
        {course.instructor_name && (
          <section style={{ padding: '72px 0', background: 'var(--bg-elevated)' }}>
            <div style={maxW}>
              <SectionHeader tag="Giảng viên" title="Người đồng hành của bạn" />
              <div style={{ display: 'flex', gap: '28px', alignItems: 'flex-start', background: 'var(--bg-card)', border: '1px solid var(--border-bright)', borderRadius: '20px', padding: '32px', boxShadow: '0 4px 32px rgba(0,212,255,0.07)', flexWrap: 'wrap' }}>
                <div style={{ width: '90px', height: '90px', borderRadius: '50%', background: 'linear-gradient(135deg,#00d4ff,#7b2fff)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '40px', flexShrink: 0 }}>
                  👨‍🏫
                </div>
                <div style={{ flex: 1, minWidth: '200px' }}>
                  <div style={{ fontSize: '22px', fontWeight: 900, color: 'var(--text)', marginBottom: '6px' }}>{course.instructor_name}</div>
                  <div style={{ fontSize: '13px', color: 'var(--neon)', marginBottom: '14px', fontWeight: 600 }}>Chuyên gia & Giảng viên</div>
                  <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap', marginBottom: '16px' }}>
                    {[
                      { v: formatNumber(course.total_students || 0) + '+', l: 'Học viên' },
                      { v: (course.avg_rating || 0).toFixed(1) + '⭐', l: 'Đánh giá' },
                      { v: String(totalLessons), l: 'Bài học' },
                    ].map(({ v, l }) => (
                      <div key={l} style={{ textAlign: 'center' }}>
                        <div style={{ fontSize: '18px', fontWeight: 900, color: 'var(--text)' }}>{v}</div>
                        <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{l}</div>
                      </div>
                    ))}
                  </div>
                  <p style={{ fontSize: '14px', color: 'var(--text-muted)', lineHeight: 1.75 }}>
                    Chuyên gia thực chiến với nhiều năm kinh nghiệm trong lĩnh vực{catName ? ` ${catName}` : ' digital marketing'}. Đã đồng hành và giúp hàng trăm học viên đạt kết quả thực tế trong công việc và kinh doanh.
                  </p>
                </div>
              </div>
            </div>
          </section>
        )}

        {/* ══════════════════════════════════════
            SECTION: REQUIREMENTS (dynamic)
        ══════════════════════════════════════ */}
        {hasRequirements && (
          <section style={{ padding: '72px 0', background: 'var(--bg)' }}>
            <div style={maxW}>
              <SectionHeader tag="Chuẩn bị" title="Yêu cầu đầu vào" sub="Những điều bạn cần có trước khi bắt đầu học" />
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {course.requirements!.map((req, i) => (
                  <div key={i} style={{ display: 'flex', gap: '12px', padding: '14px 18px', background: 'var(--bg-card)', borderRadius: '10px', border: '1px solid var(--border)', fontSize: '14px', color: 'var(--text-muted)' }}>
                    <span style={{ color: 'var(--neon)', fontWeight: 900, fontSize: '16px', flexShrink: 0 }}>›</span>
                    <span style={{ lineHeight: 1.6 }}>{req}</span>
                  </div>
                ))}
              </div>
            </div>
          </section>
        )}

        {/* ══════════════════════════════════════
            SECTION: FAQ (dynamic)
        ══════════════════════════════════════ */}
        {hasFaq && (
          <section style={{ padding: '72px 0', background: 'var(--bg-elevated)' }}>
            <div style={maxW}>
              <SectionHeader tag="Giải đáp" title="Câu hỏi thường gặp" sub="Những thắc mắc phổ biến từ học viên" />
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {course.faq!.map((item, i) => (
                  <details key={i} style={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: '12px', overflow: 'hidden' }}>
                    <summary style={{ padding: '18px 22px', fontWeight: 700, fontSize: '15px', color: 'var(--text)', listStyle: 'none', display: 'flex', justifyContent: 'space-between', alignItems: 'center', cursor: 'pointer' }}>
                      <span>{item.q}</span>
                      <span style={{ color: 'var(--neon)', fontSize: '20px', flexShrink: 0, marginLeft: '12px' }}>+</span>
                    </summary>
                    <div style={{ padding: '14px 22px 18px', borderTop: '1px solid var(--border)', fontSize: '14px', color: 'var(--text-muted)', lineHeight: 1.75 }}>
                      {item.a}
                    </div>
                  </details>
                ))}
              </div>
            </div>
          </section>
        )}

        {/* ══════════════════════════════════════
            SECTION: SOCIAL PROOF (Always shown)
        ══════════════════════════════════════ */}
        <section style={{ padding: '72px 0', background: 'var(--bg)' }}>
          <div style={maxW}>
            <SectionHeader
              tag="Học viên chia sẻ"
              title="Kết quả thực tế từ học viên"
              sub="Hàng trăm học viên đã thay đổi sự nghiệp sau khi học"
            />
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '16px' }}>
              {[
                { name: 'Nguyễn Thành Nam', role: 'Chủ doanh nghiệp', star: 5, text: `Sau khi học ${course.title}, tôi đã áp dụng được ngay vào công việc. Doanh thu tăng rõ rệt chỉ trong tháng đầu tiên!` },
                { name: 'Trần Thị Lan', role: 'Freelancer', star: 5, text: 'Giảng viên dạy rất tận tâm, nội dung thực chiến 100%. Tôi đã thu hồi học phí chỉ sau 2 tuần áp dụng.' },
                { name: 'Lê Minh Khoa', role: 'Marketing Manager', star: 5, text: 'Khóa học rất xứng đáng với số tiền bỏ ra. Học xong có thể làm được ngay, không cần tự mò mẫm nữa.' },
              ].map((t, i) => (
                <div key={i} style={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: '16px', padding: '24px' }}>
                  <div style={{ color: '#f59e0b', fontSize: '16px', marginBottom: '12px' }}>{'★'.repeat(t.star)}</div>
                  <p style={{ fontSize: '14px', color: 'var(--text-muted)', lineHeight: 1.75, marginBottom: '16px', fontStyle: 'italic' }}>
                    &quot;{t.text}&quot;
                  </p>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <div style={{ width: '36px', height: '36px', borderRadius: '50%', background: 'linear-gradient(135deg,#00d4ff,#7b2fff)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '16px' }}>
                      {t.name[0]}
                    </div>
                    <div>
                      <div style={{ fontWeight: 700, fontSize: '14px', color: 'var(--text)' }}>{t.name}</div>
                      <div style={{ fontSize: '12px', color: 'var(--text-dim)' }}>{t.role}</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ══════════════════════════════════════
            SECTION: FINAL PRICING CTA
        ══════════════════════════════════════ */}
        <CourseBuyBox course={course} totalLessons={totalLessons} totalDuration={totalDuration} />

      </main>
      <Footer />
    </>
  )
}

'use client'

import { useState, useEffect, useCallback } from 'react'
import { useParams, useRouter } from 'next/navigation'
import Link from 'next/link'
import { api } from '@/lib/api'
import { useAuth } from '@/lib/auth'
import type { Course, Lesson, Chapter } from '@/types'

/* ── helpers ── */
function fmtDuration(s?: number) {
  if (!s) return ''
  const m = Math.floor(s / 60), sec = s % 60
  return `${m}:${sec.toString().padStart(2, '0')}`
}

export default function LearnPage() {
  const { slug } = useParams<{ slug: string }>()
  const router = useRouter()
  const { isAdmin } = useAuth()

  const [course, setCourse] = useState<Course | null>(null)
  const [activeLesson, setActiveLesson] = useState<Lesson | null>(null)
  const [videoId, setVideoId] = useState<string | null>(null)
  const [loadingVideo, setLoadingVideo] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [loading, setLoading] = useState(true)

  /* ── Load course ── */
  useEffect(() => {
    api.get(`/courses/${slug}?enrolled=1`)
      .then(r => {
        const c: Course = r.data
        if (!c.is_enrolled && !isAdmin) { router.push(`/courses/${slug}`); return }
        setCourse(c)
        // Auto-select last lesson or first lesson
        const all = c.chapters?.flatMap(ch => ch.lessons || []) || []
        const last = all.find(l => l.id === c.last_lesson_id) || all[0]
        if (last) loadLesson(c.slug, last)
      })
      .catch(() => router.push('/dashboard'))
      .finally(() => setLoading(false))
  }, [slug])

  /* ── Load a lesson (get video_id) ── */
  const loadLesson = useCallback(async (courseSlug: string, lesson: Lesson) => {
    setActiveLesson(lesson)
    setVideoId(null)
    setLoadingVideo(true)
    try {
      const { data } = await api.get(`/courses/${courseSlug}/learn/${lesson.id}`)
      setVideoId(data.video_id || null)
    } catch {
      setVideoId(null)
    } finally {
      setLoadingVideo(false)
    }
  }, [])

  /* ── Mark lesson complete ── */
  const markComplete = async () => {
    if (!activeLesson || !course) return
    try {
      await api.post(`/dashboard/lessons/${activeLesson.id}/complete`)
      // update local state
      setCourse(prev => {
        if (!prev) return prev
        return {
          ...prev,
          chapters: prev.chapters?.map(ch => ({
            ...ch,
            lessons: ch.lessons?.map(l =>
              l.id === activeLesson.id ? { ...l, is_completed: true } : l
            ),
          })),
        }
      })
      setActiveLesson(prev => prev ? { ...prev, is_completed: true } : prev)
    } catch {}
  }

  /* ── Next / Prev ── */
  const allLessons = course?.chapters?.flatMap(ch => ch.lessons || []) || []
  const currentIdx = allLessons.findIndex(l => l.id === activeLesson?.id)
  const prevLesson = currentIdx > 0 ? allLessons[currentIdx - 1] : null
  const nextLesson = currentIdx < allLessons.length - 1 ? allLessons[currentIdx + 1] : null

  const completedCount = allLessons.filter(l => l.is_completed).length
  const progressPct = allLessons.length ? Math.round(completedCount / allLessons.length * 100) : 0

  /* ── Loading screen ── */
  if (loading) return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh', background: 'var(--bg)' }}>
      <div style={{ textAlign: 'center' }}>
        <span className="spinner" style={{ width: '40px', height: '40px', borderWidth: '3px' }} />
        <p style={{ color: 'var(--text-muted)', marginTop: '16px', fontSize: '14px' }}>Đang tải khóa học…</p>
      </div>
    </div>
  )
  if (!course) return null

  return (
    <div style={{ display: 'flex', height: '100vh', overflow: 'hidden', background: 'var(--bg)', fontFamily: 'inherit' }}>

      {/* ══════════ SIDEBAR ══════════ */}
      <div style={{
        width: sidebarOpen ? '320px' : '0',
        minWidth: sidebarOpen ? '320px' : '0',
        overflow: 'hidden',
        transition: 'width 0.25s, min-width 0.25s',
        borderRight: '1px solid var(--border)',
        display: 'flex', flexDirection: 'column',
        background: 'var(--bg-card)',
        flexShrink: 0,
      }}>
        {/* Sidebar header */}
        <div style={{ padding: '14px 16px', borderBottom: '1px solid var(--border)', flexShrink: 0 }}>
          <Link href="/dashboard" style={{ fontSize: '12px', color: 'var(--text-muted)', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '4px', marginBottom: '10px' }}>
            ← Về Dashboard
          </Link>
          <div style={{ fontSize: '13px', fontWeight: 700, color: 'var(--text)', lineHeight: 1.4, marginBottom: '10px' }}>
            {course.title}
          </div>
          {/* Progress */}
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: 'var(--text-muted)', marginBottom: '6px' }}>
            <span>{completedCount}/{allLessons.length} bài hoàn thành</span>
            <span style={{ color: progressPct === 100 ? '#00ff88' : 'var(--neon)', fontWeight: 700 }}>{progressPct}%</span>
          </div>
          <div style={{ height: '4px', background: 'rgba(255,255,255,0.06)', borderRadius: '2px', overflow: 'hidden' }}>
            <div style={{ height: '100%', width: `${progressPct}%`, background: progressPct === 100 ? '#00ff88' : 'linear-gradient(90deg, var(--neon), var(--neon-purple))', transition: 'width 0.4s', borderRadius: '2px' }} />
          </div>
        </div>

        {/* Lesson list */}
        <div style={{ flex: 1, overflowY: 'auto' }}>
          {course.chapters?.map((chapter: Chapter, ci: number) => (
            <div key={chapter.id}>
              {/* Chapter title */}
              <div style={{ padding: '10px 16px 8px', background: 'var(--bg-elevated)', borderBottom: '1px solid var(--border)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ width: '20px', height: '20px', borderRadius: '50%', background: 'rgba(0,212,255,0.12)', border: '1px solid rgba(0,212,255,0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '10px', fontWeight: 800, color: 'var(--neon)', flexShrink: 0 }}>
                  {ci + 1}
                </span>
                <span style={{ fontSize: '12px', fontWeight: 700, color: 'var(--text)', lineHeight: 1.4 }}>{chapter.title}</span>
              </div>

              {/* Lessons */}
              {chapter.lessons?.map((lesson: Lesson, li: number) => {
                const isActive = activeLesson?.id === lesson.id
                return (
                  <button
                    key={lesson.id}
                    onClick={() => loadLesson(course.slug, lesson)}
                    style={{
                      width: '100%', padding: '10px 14px',
                      border: 'none', borderBottom: '1px solid var(--border)',
                      background: isActive ? 'rgba(0,212,255,0.08)' : 'transparent',
                      borderLeft: isActive ? '3px solid var(--neon)' : '3px solid transparent',
                      cursor: 'pointer', display: 'flex', alignItems: 'flex-start', gap: '10px',
                      fontFamily: 'inherit', textAlign: 'left',
                      transition: 'background 0.15s',
                    }}
                  >
                    {/* Status icon */}
                    <span style={{
                      width: '22px', height: '22px', borderRadius: '50%', flexShrink: 0, marginTop: '1px',
                      background: lesson.is_completed ? 'rgba(0,255,136,0.12)' : isActive ? 'rgba(0,212,255,0.12)' : 'rgba(255,255,255,0.04)',
                      border: `1px solid ${lesson.is_completed ? 'rgba(0,255,136,0.4)' : isActive ? 'rgba(0,212,255,0.4)' : 'var(--border)'}`,
                      display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '9px',
                    }}>
                      {lesson.is_completed ? '✓' : isActive ? '▶' : String(li + 1).padStart(2, '0')}
                    </span>

                    {/* Title + duration */}
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ fontSize: '13px', color: isActive ? 'var(--text)' : lesson.is_completed ? 'var(--text-muted)' : 'var(--text-muted)', lineHeight: 1.45, fontWeight: isActive ? 600 : 400, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {lesson.title}
                      </div>
                      {lesson.duration_seconds && lesson.duration_seconds > 0 && (
                        <div style={{ fontSize: '11px', color: 'var(--text-dim)', marginTop: '2px' }}>
                          ⏱ {fmtDuration(lesson.duration_seconds)}
                        </div>
                      )}
                    </div>
                  </button>
                )
              })}
            </div>
          ))}
        </div>
      </div>

      {/* ══════════ MAIN CONTENT ══════════ */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden', minWidth: 0 }}>

        {/* Top bar */}
        <div style={{ padding: '0 16px', height: '52px', borderBottom: '1px solid var(--border)', display: 'flex', alignItems: 'center', gap: '12px', background: 'var(--bg-card)', flexShrink: 0 }}>
          <button
            onClick={() => setSidebarOpen(v => !v)}
            style={{ width: '34px', height: '34px', border: '1px solid var(--border)', background: 'var(--bg-elevated)', borderRadius: '8px', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '14px', flexShrink: 0, color: 'var(--text)' }}
            title={sidebarOpen ? 'Ẩn danh sách' : 'Hiện danh sách'}
          >
            {sidebarOpen ? '◀' : '☰'}
          </button>

          <div style={{ flex: 1, fontSize: '14px', fontWeight: 600, color: 'var(--text)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
            {activeLesson?.title || course.title}
          </div>

          {/* Prev / Next */}
          <div style={{ display: 'flex', gap: '6px', flexShrink: 0 }}>
            <button
              onClick={() => prevLesson && loadLesson(course.slug, prevLesson)}
              disabled={!prevLesson}
              style={{ padding: '6px 12px', border: '1px solid var(--border)', background: 'var(--bg-elevated)', borderRadius: '7px', cursor: prevLesson ? 'pointer' : 'not-allowed', opacity: prevLesson ? 1 : 0.3, fontSize: '12px', color: 'var(--text)', fontFamily: 'inherit' }}
            >
              ← Trước
            </button>
            <button
              onClick={() => nextLesson && loadLesson(course.slug, nextLesson)}
              disabled={!nextLesson}
              style={{ padding: '6px 12px', border: '1px solid var(--border)', background: 'var(--bg-elevated)', borderRadius: '7px', cursor: nextLesson ? 'pointer' : 'not-allowed', opacity: nextLesson ? 1 : 0.3, fontSize: '12px', color: 'var(--text)', fontFamily: 'inherit' }}
            >
              Sau →
            </button>
          </div>
        </div>

        {/* Video area */}
        <div style={{ flex: 1, background: '#000', display: 'flex', alignItems: 'center', justifyContent: 'center', position: 'relative', overflow: 'hidden' }}>
          {loadingVideo ? (
            <div style={{ textAlign: 'center' }}>
              <span className="spinner" style={{ width: '36px', height: '36px', borderWidth: '3px', borderColor: 'rgba(255,255,255,0.2)', borderTopColor: 'var(--neon)' }} />
              <p style={{ color: 'rgba(255,255,255,0.4)', marginTop: '14px', fontSize: '13px' }}>Đang tải bài học…</p>
            </div>
          ) : videoId ? (
            <div style={{ width: '100%', height: '100%', position: 'relative' }}>
              <iframe
                key={videoId}
                src={`https://www.youtube.com/embed/${videoId}?autoplay=1&rel=0&modestbranding=1`}
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; fullscreen"
                allowFullScreen
                style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', border: 'none' }}
              />
            </div>
          ) : (
            <div style={{ textAlign: 'center', padding: '48px' }}>
              <div style={{ fontSize: '56px', marginBottom: '16px', opacity: 0.4 }}>🎬</div>
              <p style={{ color: 'rgba(255,255,255,0.4)', fontSize: '16px', marginBottom: '8px' }}>
                {activeLesson ? 'Bài học này chưa có video' : 'Chọn bài học từ danh sách bên trái'}
              </p>
              {activeLesson && !videoId && (
                <p style={{ color: 'rgba(255,255,255,0.2)', fontSize: '13px' }}>Liên hệ giảng viên nếu bạn không thấy nội dung</p>
              )}
            </div>
          )}
        </div>

        {/* Bottom info bar */}
        <div style={{ padding: '14px 20px', borderTop: '1px solid var(--border)', background: 'var(--bg-card)', flexShrink: 0, display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '16px', flexWrap: 'wrap' }}>
          <div>
            <div style={{ fontSize: '15px', fontWeight: 700, color: 'var(--text)', marginBottom: '2px' }}>
              {activeLesson?.title}
            </div>
            {activeLesson?.duration_seconds && activeLesson.duration_seconds > 0 && (
              <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                ⏱ {fmtDuration(activeLesson.duration_seconds)}
                {currentIdx >= 0 && <span style={{ marginLeft: '12px' }}>Bài {currentIdx + 1}/{allLessons.length}</span>}
              </div>
            )}
          </div>

          <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
            {activeLesson?.is_completed ? (
              <span style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '7px 14px', borderRadius: '8px', background: 'rgba(0,255,136,0.08)', border: '1px solid rgba(0,255,136,0.25)', fontSize: '13px', color: '#00ff88', fontWeight: 600 }}>
                ✓ Đã hoàn thành
              </span>
            ) : (
              <button
                className="btn btn-primary btn-sm"
                onClick={markComplete}
                style={{ fontSize: '13px' }}
              >
                ✓ Đánh dấu hoàn thành
              </button>
            )}
            {nextLesson && (
              <button
                className="btn btn-ghost btn-sm"
                onClick={() => loadLesson(course.slug, nextLesson)}
                style={{ fontSize: '13px' }}
              >
                Bài tiếp theo →
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

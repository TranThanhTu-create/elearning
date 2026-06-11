'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import Link from 'next/link'
import { api, extractError } from '@/lib/api'
import { formatDuration } from '@/lib/utils'
import type { Course, Lesson } from '@/types'

export default function LearnPage() {
  const { slug } = useParams<{ slug: string }>()
  const router = useRouter()
  const [course, setCourse] = useState<Course | null>(null)
  const [activeLesson, setActiveLesson] = useState<Lesson | null>(null)
  const [loading, setLoading] = useState(true)
  const [sidebarOpen, setSidebarOpen] = useState(true)

  useEffect(() => {
    api.get(`/courses/${slug}?enrolled=1`).then(r => {
      const c: Course = r.data
      if (!c.is_enrolled) { router.push(`/courses/${slug}`); return }
      setCourse(c)
      const firstLesson = c.chapters?.[0]?.lessons?.[0]
      if (firstLesson) setActiveLesson(firstLesson)
    }).catch(() => router.push('/dashboard')).finally(() => setLoading(false))
  }, [slug])

  const markComplete = async (lessonId: string) => {
    try {
      await api.post(`/dashboard/lessons/${lessonId}/complete`)
      // refresh course to update progress
      const { data } = await api.get(`/courses/${slug}?enrolled=1`)
      setCourse(data)
    } catch {}
  }

  if (loading) return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh' }}>
      <span className="spinner" style={{ width: '36px', height: '36px', borderWidth: '3px' }} />
    </div>
  )

  if (!course) return null

  const allLessons = course.chapters?.flatMap(c => c.lessons || []) || []
  const completedCount = allLessons.filter(l => l.is_completed).length

  return (
    <div style={{ display: 'flex', height: '100vh', overflow: 'hidden' }}>
      {/* Sidebar */}
      {sidebarOpen && (
        <div style={{ width: '320px', borderRight: '2px solid #111', overflow: 'auto', background: '#fff', flexShrink: 0 }}>
          <div style={{ padding: '16px', borderBottom: '1px solid #eee', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Link href="/dashboard" style={{ fontSize: '14px', fontWeight: 700, color: '#111', textDecoration: 'none' }}>← Dashboard</Link>
            <button onClick={() => setSidebarOpen(false)} style={{ border: 'none', background: 'none', cursor: 'pointer', fontSize: '18px' }}>✕</button>
          </div>
          <div style={{ padding: '12px 16px', borderBottom: '1px solid #eee' }}>
            <div style={{ fontSize: '13px', fontWeight: 700, marginBottom: '6px' }}>{course.title}</div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', color: '#888', marginBottom: '4px' }}>
              <span>{completedCount}/{allLessons.length} bài</span>
              <span>{course.chapters?.reduce((s, c) => s + (c.lessons?.length || 0), 0) || 0} bài học</span>
            </div>
            <div className="progress">
              <div className="progress-fill progress-fill-success" style={{ width: `${allLessons.length ? completedCount / allLessons.length * 100 : 0}%` }} />
            </div>
          </div>

          {course.chapters?.map(chapter => (
            <div key={chapter.id}>
              <div style={{ padding: '10px 16px', background: '#f6f6f6', fontSize: '13px', fontWeight: 700, borderBottom: '1px solid #eee' }}>
                {chapter.title}
              </div>
              {chapter.lessons?.map(lesson => (
                <button
                  key={lesson.id}
                  onClick={() => setActiveLesson(lesson)}
                  style={{
                    width: '100%', padding: '10px 16px', border: 'none', background: activeLesson?.id === lesson.id ? '#111' : '#fff',
                    color: activeLesson?.id === lesson.id ? '#fff' : '#333',
                    cursor: 'pointer', display: 'flex', alignItems: 'flex-start', gap: '8px',
                    fontSize: '13px', textAlign: 'left', fontFamily: 'inherit', borderBottom: '1px solid #eee',
                  }}
                >
                  <span style={{ marginTop: '1px', flexShrink: 0 }}>{lesson.is_completed ? '✅' : '▶'}</span>
                  <div style={{ flex: 1 }}>
                    <div style={{ lineHeight: 1.4 }}>{lesson.title}</div>
                    {lesson.duration_seconds && <div style={{ fontSize: '11px', opacity: 0.7, marginTop: '2px' }}>{formatDuration(lesson.duration_seconds)}</div>}
                  </div>
                </button>
              ))}
            </div>
          ))}
        </div>
      )}

      {/* Main content */}
      <div style={{ flex: 1, overflow: 'auto', display: 'flex', flexDirection: 'column' }}>
        {/* Top bar */}
        <div style={{ padding: '12px 20px', borderBottom: '1px solid #eee', display: 'flex', alignItems: 'center', gap: '12px', background: '#fff', flexShrink: 0 }}>
          {!sidebarOpen && (
            <button onClick={() => setSidebarOpen(true)} style={{ border: '1.5px solid #111', background: 'none', borderRadius: '6px', padding: '6px 10px', cursor: 'pointer', fontFamily: 'inherit', fontWeight: 600 }}>
              ☰ Bài học
            </button>
          )}
          <div style={{ fontSize: '14px', fontWeight: 600 }}>{activeLesson?.title || course.title}</div>
        </div>

        {/* Video area */}
        <div style={{ flex: 1, background: '#000', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          {activeLesson?.video_url ? (
            <video
              key={activeLesson.id}
              controls
              style={{ width: '100%', maxHeight: '70vh' }}
              onEnded={() => activeLesson && markComplete(activeLesson.id)}
            >
              <source src={activeLesson.video_url} />
            </video>
          ) : (
            <div style={{ textAlign: 'center', color: '#666', padding: '48px' }}>
              <div style={{ fontSize: '48px', marginBottom: '16px' }}>🎬</div>
              <p style={{ fontSize: '16px' }}>Chọn bài học từ danh sách bên trái để bắt đầu</p>
            </div>
          )}
        </div>

        {/* Lesson info */}
        {activeLesson && (
          <div style={{ padding: '20px', borderTop: '1px solid #eee', background: '#fff' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <h2 style={{ fontSize: '18px', fontWeight: 700 }}>{activeLesson.title}</h2>
                {activeLesson.duration_seconds && <p style={{ color: '#666', fontSize: '14px', marginTop: '4px' }}>Thời lượng: {formatDuration(activeLesson.duration_seconds)}</p>}
              </div>
              {!activeLesson.is_completed && (
                <button className="btn btn-primary" onClick={() => markComplete(activeLesson.id)}>
                  Đánh dấu hoàn thành ✓
                </button>
              )}
              {activeLesson.is_completed && (
                <span className="tag tag-success" style={{ fontSize: '13px', padding: '6px 12px' }}>✓ Đã hoàn thành</span>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

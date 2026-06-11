'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import Navbar from '@/components/layout/Navbar'
import Footer from '@/components/layout/Footer'
import { api } from '@/lib/api'
import { useAuth } from '@/lib/auth'
import { formatDate, formatDuration } from '@/lib/utils'
import type { DashboardCourse } from '@/types'

export default function DashboardPage() {
  const { user, loading: authLoading } = useAuth()
  const [courses, setCourses] = useState<DashboardCourse[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (authLoading) return
    api.get('/dashboard/my-courses').then(r => setCourses(r.data)).catch(() => {}).finally(() => setLoading(false))
  }, [authLoading])

  if (authLoading || loading) return (
    <>
      <Navbar />
      <div className="container section">
        <div className="grid-3">
          {Array.from({ length: 3 }).map((_, i) => <div key={i} className="skeleton" style={{ height: '200px' }} />)}
        </div>
      </div>
      <Footer />
    </>
  )

  const inProgress = courses.filter(c => !c.is_completed)
  const completed = courses.filter(c => c.is_completed)

  return (
    <>
      <Navbar />
      <main style={{ flex: 1 }}>
        <div style={{ background: '#f6f6f6', borderBottom: '1px solid #eee', padding: '24px 0' }}>
          <div className="container">
            <h1 style={{ fontSize: '22px', fontWeight: 800 }}>Xin chào, {user?.name}!</h1>
            <p style={{ color: '#666', marginTop: '4px' }}>Tiếp tục hành trình học tập của bạn</p>
          </div>
        </div>

        <div className="section-sm">
          <div className="container">
            {/* Nav */}
            <div className="tabs" style={{ marginBottom: '24px' }}>
              <Link href="/dashboard" className="tab active">Khóa học ({courses.length})</Link>
              <Link href="/dashboard/profile" className="tab">Hồ sơ</Link>
              <Link href="/dashboard/affiliate" className="tab">Affiliate</Link>
            </div>

            {courses.length === 0 ? (
              <div className="empty-state">
                <div className="empty-state-icon">📚</div>
                <div className="empty-state-text">Bạn chưa có khóa học nào</div>
                <Link href="/courses" className="btn btn-primary" style={{ marginTop: '16px' }}>Khám phá khóa học</Link>
              </div>
            ) : (
              <>
                {inProgress.length > 0 && (
                  <div style={{ marginBottom: '32px' }}>
                    <h2 style={{ fontSize: '17px', fontWeight: 700, marginBottom: '16px' }}>Đang học ({inProgress.length})</h2>
                    <div className="grid-3">
                      {inProgress.map(c => <EnrolledCourseCard key={c.id} course={c} />)}
                    </div>
                  </div>
                )}
                {completed.length > 0 && (
                  <div>
                    <h2 style={{ fontSize: '17px', fontWeight: 700, marginBottom: '16px' }}>Đã hoàn thành ({completed.length})</h2>
                    <div className="grid-3">
                      {completed.map(c => <EnrolledCourseCard key={c.id} course={c} />)}
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </main>
      <Footer />
    </>
  )
}

function EnrolledCourseCard({ course }: { course: DashboardCourse }) {
  return (
    <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
      <div style={{ position: 'relative', height: '140px', background: '#e8e8e8' }}>
        {course.thumbnail_url
          ? <img src={course.thumbnail_url} alt={course.title} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
          : <div style={{ width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '36px' }}>🎓</div>
        }
        {course.is_completed && (
          <div style={{ position: 'absolute', top: 8, right: 8, background: '#27ae60', color: '#fff', fontSize: '11px', fontWeight: 700, padding: '3px 8px', borderRadius: '4px' }}>Hoàn thành</div>
        )}
      </div>
      <div style={{ padding: '14px' }}>
        <div style={{ fontSize: '14px', fontWeight: 700, marginBottom: '8px', lineHeight: 1.4 }}>{course.title}</div>
        <div style={{ marginBottom: '10px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', color: '#888', marginBottom: '4px' }}>
            <span>Tiến độ</span>
            <span>{course.progress_percent}%</span>
          </div>
          <div className="progress">
            <div className={`progress-fill${course.is_completed ? ' progress-fill-success' : ''}`} style={{ width: `${course.progress_percent}%` }} />
          </div>
        </div>
        <Link href={`/learn/${course.slug}`} className="btn btn-primary btn-full btn-sm">
          {course.progress_percent > 0 ? 'Tiếp tục học →' : 'Bắt đầu học →'}
        </Link>
      </div>
    </div>
  )
}

'use client'

import { useState, useEffect, useCallback } from 'react'
import Navbar from '@/components/layout/Navbar'
import Footer from '@/components/layout/Footer'
import CourseCard from '@/components/features/CourseCard'
import Pagination from '@/components/ui/Pagination'
import { api } from '@/lib/api'
import type { Course, Category, PaginatedResponse } from '@/types'

export default function CoursesPage() {
  const [courses, setCourses] = useState<Course[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [catSlug, setCatSlug] = useState('')
  const [level, setLevel] = useState('')
  const [sort, setSort] = useState('popular')
  const [loading, setLoading] = useState(true)
  const pageSize = 12

  useEffect(() => {
    api.get('/courses/categories').then(r => setCategories(r.data)).catch(() => {})
  }, [])

  const fetchCourses = useCallback(async (p = 1) => {
    setLoading(true)
    try {
      const params: Record<string, string | number> = { page: p, page_size: pageSize, sort }
      if (search) params.q = search
      if (catSlug) params.category = catSlug
      if (level) params.level = level
      const { data } = await api.get<PaginatedResponse<Course>>('/courses', { params })
      setCourses(data.items)
      setTotal(data.total)
      setPage(p)
    } catch { setCourses([]) }
    finally { setLoading(false) }
  }, [search, catSlug, level, sort])

  useEffect(() => { fetchCourses(1) }, [fetchCourses])
  const totalPages = Math.ceil(total / pageSize)

  return (
    <>
      <Navbar />
      <main style={{ flex: 1 }}>
        {/* Hero banner */}
        <div style={{
          background: 'radial-gradient(ellipse 90% 60% at 50% 0%, rgba(0,212,255,0.12) 0%, transparent 65%), var(--bg)',
          borderBottom: '1px solid var(--border)', padding: '48px 0 40px',
          position: 'relative', overflow: 'hidden',
        }}>
          <div style={{ position: 'absolute', inset: 0, backgroundImage: 'linear-gradient(rgba(0,212,255,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(0,212,255,0.03) 1px, transparent 1px)', backgroundSize: '60px 60px', pointerEvents: 'none' }} />
          <div className="container" style={{ position: 'relative' }}>
            <div style={{ fontSize: '12px', fontWeight: 700, color: 'var(--neon)', textTransform: 'uppercase', letterSpacing: '1.5px', marginBottom: '10px' }}>Khóa học</div>
            <h1 style={{ fontSize: 'clamp(24px, 3.5vw, 38px)', fontWeight: 900, color: 'var(--text)', letterSpacing: '-0.5px', marginBottom: '8px' }}>
              Tất cả khóa học{' '}
              <span style={{ background: 'linear-gradient(135deg, #00d4ff, #7b2fff)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>
                AI Agent & Marketing
              </span>
            </h1>
            <p style={{ color: 'var(--text-muted)', fontSize: '15px' }}>Khám phá {total} khóa học thực chiến từ chuyên gia</p>
          </div>
        </div>

        <div className="section-sm">
          <div className="container">
            {/* Filter bar */}
            <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', marginBottom: '20px', alignItems: 'center' }}>
              <input
                className="form-input"
                placeholder="🔍 Tìm kiếm khóa học..."
                value={search}
                onChange={e => setSearch(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && fetchCourses(1)}
                style={{ maxWidth: '280px', flex: '1 1 200px' }}
              />
              <select className="form-input" value={level} onChange={e => setLevel(e.target.value)} style={{ maxWidth: '160px', flex: '1 1 130px' }}>
                <option value="">Tất cả cấp độ</option>
                <option value="beginner">Cơ bản</option>
                <option value="intermediate">Trung cấp</option>
                <option value="advanced">Nâng cao</option>
              </select>
              <select className="form-input" value={sort} onChange={e => setSort(e.target.value)} style={{ maxWidth: '180px', flex: '1 1 150px' }}>
                <option value="popular">Phổ biến nhất</option>
                <option value="newest">Mới nhất</option>
                <option value="rating">Đánh giá cao</option>
                <option value="price_asc">Giá thấp → cao</option>
                <option value="price_desc">Giá cao → thấp</option>
              </select>
              <button className="btn btn-primary btn-sm" onClick={() => fetchCourses(1)}>Tìm kiếm</button>
            </div>

            {/* Category pills */}
            {categories.length > 0 && (
              <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: '28px' }}>
                {[{ slug: '', name: 'Tất cả' }, ...categories].map(c => (
                  <button
                    key={c.slug}
                    onClick={() => setCatSlug(c.slug)}
                    style={{
                      padding: '6px 14px', borderRadius: '100px', fontSize: '13px', fontWeight: 600, cursor: 'pointer', border: 'none', transition: 'all 0.15s',
                      background: catSlug === c.slug ? 'var(--neon)' : 'var(--bg-elevated)',
                      color: catSlug === c.slug ? '#070b14' : 'var(--text-muted)',
                      boxShadow: catSlug === c.slug ? '0 0 12px rgba(0,212,255,0.4)' : 'none',
                    }}
                  >
                    {c.name}
                  </button>
                ))}
              </div>
            )}

            {/* Results */}
            {loading ? (
              <div className="grid-4">
                {Array.from({ length: 8 }).map((_, i) => (
                  <div key={i}>
                    <div className="skeleton" style={{ height: '160px', marginBottom: '8px' }} />
                    <div className="skeleton" style={{ height: '20px', marginBottom: '6px' }} />
                    <div className="skeleton" style={{ height: '14px', width: '60%' }} />
                  </div>
                ))}
              </div>
            ) : courses.length > 0 ? (
              <>
                <div className="grid-4">
                  {courses.map(c => <CourseCard key={c.id} course={c} />)}
                </div>
                <Pagination page={page} totalPages={totalPages} onPageChange={fetchCourses} />
              </>
            ) : (
              <div style={{ textAlign: 'center', padding: '64px 0' }}>
                <div style={{ fontSize: '48px', marginBottom: '16px' }}>🔍</div>
                <div style={{ fontSize: '16px', color: 'var(--text-muted)' }}>Không tìm thấy khóa học phù hợp</div>
                <button className="btn btn-ghost btn-sm" onClick={() => { setSearch(''); setCatSlug(''); setLevel('') }} style={{ marginTop: '16px' }}>
                  Xóa bộ lọc
                </button>
              </div>
            )}
          </div>
        </div>
      </main>
      <Footer />
    </>
  )
}

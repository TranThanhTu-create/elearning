'use client'

import { useState, useEffect, useCallback } from 'react'
import Link from 'next/link'
import { api, extractError } from '@/lib/api'
import { formatVnd, formatNumber, formatDate } from '@/lib/utils'
import Pagination from '@/components/ui/Pagination'
import type { Course, PaginatedResponse } from '@/types'

export default function AdminCoursesPage() {
  const [courses, setCourses] = useState<Course[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const fetch = useCallback(async (p = 1) => {
    setLoading(true)
    try {
      const params: Record<string, string | number> = { page: p, page_size: 20 }
      if (search) params.q = search
      const { data } = await api.get<PaginatedResponse<Course>>('/admin/courses', { params })
      setCourses(data.items)
      setTotal(data.total)
      setPage(p)
    } catch { setCourses([]) }
    finally { setLoading(false) }
  }, [search])

  useEffect(() => { fetch(1) }, [fetch])

  const togglePublish = async (courseId: string) => {
    try {
      await api.patch(`/admin/courses/${courseId}/publish`)
      await fetch(page)
    } catch (err) { setError(extractError(err)) }
  }

  const deleteCourse = async (courseId: string, title: string) => {
    if (!confirm(`Xóa khóa học "${title}"?`)) return
    try {
      await api.delete(`/admin/courses/${courseId}`)
      await fetch(page)
    } catch (err) { setError(extractError(err)) }
  }

  return (
    <>
      <div className="admin-header">
        <h1>Khóa học</h1>
        <Link href="/admin/courses/new" className="btn btn-primary btn-sm">+ Thêm khóa học</Link>
      </div>
      <div className="admin-body">
        {error && <div className="alert alert-error">{error}</div>}
        <div className="filter-bar">
          <input className="form-input" placeholder="Tìm khóa học..." value={search} onChange={e => setSearch(e.target.value)} onKeyDown={e => e.key === 'Enter' && fetch(1)} style={{ maxWidth: '280px' }} />
          <button className="btn btn-primary btn-sm" onClick={() => fetch(1)}>Tìm</button>
        </div>

        {loading ? <div className="skeleton" style={{ height: '400px' }} /> : (
          <div className="card" style={{ padding: 0 }}>
            <div className="table-wrap">
              <table>
                <thead><tr><th>Khóa học</th><th>Giá</th><th>HV</th><th>Rating</th><th>Trạng thái</th><th>Ngày tạo</th><th>Thao tác</th></tr></thead>
                <tbody>
                  {courses.map(c => (
                    <tr key={c.id}>
                      <td>
                        <div style={{ fontWeight: 600, maxWidth: '240px' }}>{c.title}</div>
                        {c.category && <div style={{ fontSize: '11px', color: '#888' }}>{c.category.name}</div>}
                      </td>
                      <td>{formatVnd(c.price)}</td>
                      <td>{formatNumber(c.total_students)}</td>
                      <td>⭐ {(c.avg_rating ?? 0).toFixed(1)}</td>
                      <td>
                        <span className={`tag ${c.is_published ? 'tag-success' : 'tag-default'}`}>
                          {c.is_published ? 'Đã xuất bản' : 'Nháp'}
                        </span>
                      </td>
                      <td style={{ fontSize: '12px', color: '#888' }}>{formatDate(c.created_at)}</td>
                      <td>
                        <div style={{ display: 'flex', gap: '4px' }}>
                          <Link href={`/admin/courses/${c.id}`} className="btn btn-ghost btn-sm">Sửa</Link>
                          <button className={`btn btn-sm ${c.is_published ? 'btn-ghost' : 'btn-primary'}`} onClick={() => togglePublish(c.id)}>
                            {c.is_published ? 'Ẩn' : 'Xuất bản'}
                          </button>
                          <button className="btn btn-danger btn-sm" onClick={() => deleteCourse(c.id, c.title)}>Xóa</button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {courses.length === 0 && <div className="empty-state">Chưa có khóa học nào</div>}
            </div>
          </div>
        )}
        <Pagination page={page} totalPages={Math.ceil(total / 20)} onPageChange={fetch} />
      </div>
    </>
  )
}

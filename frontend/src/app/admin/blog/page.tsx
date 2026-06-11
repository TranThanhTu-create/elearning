'use client'

import { useState, useEffect, useCallback } from 'react'
import Link from 'next/link'
import { api, extractError } from '@/lib/api'
import { formatDate } from '@/lib/utils'
import Pagination from '@/components/ui/Pagination'
import type { BlogPost, PaginatedResponse } from '@/types'

export default function AdminBlogPage() {
  const [posts, setPosts] = useState<BlogPost[]>([])
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
      const { data } = await api.get('/admin/blog', { params })
      setPosts(data.items)
      setTotal(data.total)
      setPage(p)
    } catch { setPosts([]) }
    finally { setLoading(false) }
  }, [search])

  useEffect(() => { fetch(1) }, [fetch])

  const togglePublish = async (postId: string) => {
    try { await api.patch(`/admin/blog/${postId}/publish`); await fetch(page) }
    catch (err) { setError(extractError(err)) }
  }

  const deletePost = async (postId: string, title: string) => {
    if (!confirm(`Xóa bài viết "${title}"?`)) return
    try { await api.delete(`/admin/blog/${postId}`); await fetch(page) }
    catch (err) { setError(extractError(err)) }
  }

  return (
    <>
      <div className="admin-header">
        <h1>Blog</h1>
        <Link href="/admin/blog/new" className="btn btn-primary btn-sm">+ Viết bài</Link>
      </div>
      <div className="admin-body">
        {error && <div className="alert alert-error">{error}</div>}
        <div className="filter-bar">
          <input className="form-input" placeholder="Tìm bài viết..." value={search} onChange={e => setSearch(e.target.value)} onKeyDown={e => e.key === 'Enter' && fetch(1)} style={{ maxWidth: '280px' }} />
          <button className="btn btn-primary btn-sm" onClick={() => fetch(1)}>Tìm</button>
        </div>
        {loading ? <div className="skeleton" style={{ height: '400px' }} /> : (
          <div className="card" style={{ padding: 0 }}>
            <div className="table-wrap">
              <table>
                <thead><tr><th>Tiêu đề</th><th>Danh mục</th><th>Trạng thái</th><th>Lượt xem</th><th>Ngày</th><th>Thao tác</th></tr></thead>
                <tbody>
                  {posts.map(p => (
                    <tr key={p.id}>
                      <td style={{ maxWidth: '260px' }}>
                        <div style={{ fontWeight: 600 }}>{p.title}</div>
                        <div style={{ fontSize: '11px', color: '#888', fontFamily: 'monospace' }}>{p.slug}</div>
                      </td>
                      <td style={{ fontSize: '13px' }}>{p.category?.name || '—'}</td>
                      <td><span className={`tag ${p.status === 'published' ? 'tag-success' : 'tag-default'}`}>{p.status === 'published' ? 'Đã xuất bản' : 'Nháp'}</span></td>
                      <td>{p.view_count || 0}</td>
                      <td style={{ fontSize: '12px', color: '#888' }}>{formatDate(p.published_at || p.created_at)}</td>
                      <td>
                        <div style={{ display: 'flex', gap: '4px' }}>
                          <Link href={`/admin/blog/${p.id}`} className="btn btn-ghost btn-sm">Sửa</Link>
                          <button className={`btn btn-sm ${p.status === 'published' ? 'btn-ghost' : 'btn-primary'}`} onClick={() => togglePublish(p.id)}>
                            {p.status === 'published' ? 'Ẩn' : 'Xuất bản'}
                          </button>
                          <button className="btn btn-danger btn-sm" onClick={() => deletePost(p.id, p.title)}>Xóa</button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {posts.length === 0 && <div className="empty-state">Chưa có bài viết nào</div>}
            </div>
          </div>
        )}
        <Pagination page={page} totalPages={Math.ceil(total / 20)} onPageChange={fetch} />
      </div>
    </>
  )
}

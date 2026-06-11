'use client'

import { useState, useEffect, useCallback } from 'react'
import Navbar from '@/components/layout/Navbar'
import Footer from '@/components/layout/Footer'
import BlogCard from '@/components/features/BlogCard'
import Pagination from '@/components/ui/Pagination'
import { api } from '@/lib/api'
import type { BlogPost, BlogCategory, PaginatedResponse } from '@/types'

export default function BlogPage() {
  const [posts, setPosts] = useState<BlogPost[]>([])
  const [categories, setCategories] = useState<BlogCategory[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [catSlug, setCatSlug] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/blog/categories').then(r => setCategories(r.data)).catch(() => {})
  }, [])

  const fetch = useCallback(async (p = 1) => {
    setLoading(true)
    try {
      const params: Record<string, string | number> = { page: p, page_size: 12 }
      if (catSlug) params.category = catSlug
      const { data } = await api.get<PaginatedResponse<BlogPost>>('/blog/posts', { params })
      setPosts(data.items)
      setTotal(data.total)
      setPage(p)
    } catch { setPosts([]) }
    finally { setLoading(false) }
  }, [catSlug])

  useEffect(() => { fetch(1) }, [fetch])

  return (
    <>
      <Navbar />
      <main style={{ flex: 1 }}>
        <div style={{ background: '#111', color: '#fff', padding: '40px 0' }}>
          <div className="container">
            <h1 style={{ fontSize: '28px', fontWeight: 800, marginBottom: '8px' }}>Blog</h1>
            <p style={{ color: '#aaa' }}>Kiến thức và kinh nghiệm từ chuyên gia</p>
          </div>
        </div>

        <div className="section-sm">
          <div className="container">
            <div className="cat-pills">
              <button className={`cat-pill${catSlug === '' ? ' active' : ''}`} onClick={() => setCatSlug('')}>Tất cả</button>
              {categories.map(c => (
                <button key={c.id} className={`cat-pill${catSlug === c.slug ? ' active' : ''}`} onClick={() => setCatSlug(c.slug)}>
                  {c.name}
                </button>
              ))}
            </div>

            {loading ? (
              <div className="grid-3">
                {Array.from({ length: 6 }).map((_, i) => (
                  <div key={i}>
                    <div className="skeleton" style={{ height: '160px', marginBottom: '8px' }} />
                    <div className="skeleton" style={{ height: '18px', marginBottom: '6px' }} />
                    <div className="skeleton" style={{ height: '14px', width: '80%' }} />
                  </div>
                ))}
              </div>
            ) : posts.length > 0 ? (
              <>
                <div className="grid-3">
                  {posts.map(p => <BlogCard key={p.id} post={p} />)}
                </div>
                <Pagination page={page} totalPages={Math.ceil(total / 12)} onPageChange={fetch} />
              </>
            ) : (
              <div className="empty-state">
                <div className="empty-state-icon">📝</div>
                <div className="empty-state-text">Chưa có bài viết nào</div>
              </div>
            )}
          </div>
        </div>
      </main>
      <Footer />
    </>
  )
}

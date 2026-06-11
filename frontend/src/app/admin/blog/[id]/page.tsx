'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import Link from 'next/link'
import { api, extractError } from '@/lib/api'
import type { BlogCategory } from '@/types'

export default function AdminBlogEditPage() {
  const { id } = useParams<{ id: string }>()
  const router = useRouter()
  const isNew = id === 'new'
  const [categories, setCategories] = useState<BlogCategory[]>([])
  const [form, setForm] = useState({ title: '', slug: '', excerpt: '', content: '', thumbnail_url: '', category_id: '', author_name: '', tags: '' })
  const [loading, setLoading] = useState(!isNew)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  useEffect(() => {
    api.get('/admin/blog/categories').then(r => setCategories(r.data.items || r.data)).catch(() => {})
    if (!isNew) {
      api.get(`/admin/blog/${id}`).then(r => {
        const p = r.data
        setForm({ title: p.title || '', slug: p.slug || '', excerpt: p.excerpt || '', content: p.content || '', thumbnail_url: p.thumbnail_url || '', category_id: p.category_id || '', author_name: p.author_name || '', tags: (p.tags || []).map((t: { name: string }) => t.name).join(', ') })
      }).catch(() => {}).finally(() => setLoading(false))
    }
  }, [id, isNew])

  const set = (k: string) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => setForm(f => ({ ...f, [k]: e.target.value }))

  const save = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    setError('')
    setSuccess('')
    try {
      const body = { ...form, tags: form.tags ? form.tags.split(',').map(t => t.trim()).filter(Boolean) : [] }
      if (isNew) {
        const { data } = await api.post('/admin/blog', body)
        router.push(`/admin/blog/${data.id}`)
      } else {
        await api.patch(`/admin/blog/${id}`, body)
        setSuccess('Lưu thành công!')
      }
    } catch (err) {
      setError(extractError(err))
    } finally {
      setSaving(false)
    }
  }

  if (loading) return <div className="admin-body"><div className="skeleton" style={{ height: '400px' }} /></div>

  return (
    <>
      <div className="admin-header">
        <div>
          <Link href="/admin/blog" style={{ fontSize: '13px', color: '#666', textDecoration: 'none' }}>← Danh sách</Link>
          <h1 style={{ marginTop: '4px' }}>{isNew ? 'Viết bài mới' : 'Chỉnh sửa bài viết'}</h1>
        </div>
        {!isNew && (
          <button className="btn btn-primary btn-sm" onClick={async () => {
            try { await api.patch(`/admin/blog/${id}/publish`); setSuccess('Đã cập nhật trạng thái!') }
            catch (err) { setError(extractError(err)) }
          }}>Xuất bản / Ẩn</button>
        )}
      </div>
      <div className="admin-body">
        {error && <div className="alert alert-error">{error}</div>}
        {success && <div className="alert alert-success">{success}</div>}
        <form onSubmit={save}>
          <div className="grid-2" style={{ gap: '20px', alignItems: 'start' }}>
            <div>
              <div className="card" style={{ marginBottom: '16px' }}>
                <div className="form-group">
                  <label className="form-label">Tiêu đề *</label>
                  <input className="form-input" value={form.title} onChange={set('title')} required />
                </div>
                <div className="form-group">
                  <label className="form-label">Slug</label>
                  <input className="form-input" value={form.slug} onChange={set('slug')} placeholder="tu-dong-tao" />
                </div>
                <div className="form-group">
                  <label className="form-label">Mô tả ngắn (excerpt)</label>
                  <textarea className="form-input" value={form.excerpt} onChange={set('excerpt')} rows={2} style={{ resize: 'vertical' }} />
                </div>
                <div className="form-group">
                  <label className="form-label">Nội dung (HTML)</label>
                  <textarea className="form-input" value={form.content} onChange={set('content')} rows={16} style={{ resize: 'vertical', fontFamily: 'monospace', fontSize: '13px' }} />
                </div>
              </div>
            </div>
            <div>
              <div className="card">
                <div className="form-group">
                  <label className="form-label">Danh mục</label>
                  <select className="form-input" value={form.category_id} onChange={set('category_id')}>
                    <option value="">-- Chọn danh mục --</option>
                    {categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                  </select>
                </div>
                <div className="form-group">
                  <label className="form-label">Tác giả</label>
                  <input className="form-input" value={form.author_name} onChange={set('author_name')} placeholder="Nguyễn Văn A" />
                </div>
                <div className="form-group">
                  <label className="form-label">Tags (phân cách bằng dấu phẩy)</label>
                  <input className="form-input" value={form.tags} onChange={set('tags')} placeholder="marketing, seo, facebook" />
                </div>
                <div className="form-group">
                  <label className="form-label">URL ảnh bìa</label>
                  <input className="form-input" value={form.thumbnail_url} onChange={set('thumbnail_url')} placeholder="https://..." />
                  {form.thumbnail_url && <img src={form.thumbnail_url} alt="preview" style={{ width: '100%', marginTop: '8px', borderRadius: '6px', aspectRatio: '16/9', objectFit: 'cover' }} />}
                </div>
                <button type="submit" className="btn btn-primary btn-full" disabled={saving}>
                  {saving ? <span className="spinner" /> : isNew ? 'Tạo bài viết' : 'Lưu thay đổi'}
                </button>
              </div>
            </div>
          </div>
        </form>
      </div>
    </>
  )
}

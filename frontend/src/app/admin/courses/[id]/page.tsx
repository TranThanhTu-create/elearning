'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import Link from 'next/link'
import { api, extractError } from '@/lib/api'
import type { Course, Category, Chapter, Lesson } from '@/types'

export default function AdminCourseEditPage() {
  const { id } = useParams<{ id: string }>()
  const router = useRouter()
  const isNew = id === 'new'

  const [categories, setCategories] = useState<Category[]>([])
  const [form, setForm] = useState({ title: '', slug: '', short_desc: '', description: '', price: '', original_price: '', thumbnail_url: '', level: 'beginner', language: 'vi', category_id: '', instructor_name: '' })
  const [chapters, setChapters] = useState<Chapter[]>([])
  const [loading, setLoading] = useState(!isNew)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  useEffect(() => {
    api.get('/admin/courses/categories').then(r => setCategories(r.data.items || r.data)).catch(() => {})
    if (!isNew) {
      api.get(`/admin/courses/${id}`).then(r => {
        const c = r.data
        setForm({
          title: c.title || '',
          slug: c.slug || '',
          short_desc: c.short_desc || '',
          description: c.description || '',
          price: String(c.price || ''),
          original_price: String(c.original_price || ''),
          thumbnail_url: c.thumbnail_url || '',
          level: c.level || 'beginner',
          language: c.language || 'vi',
          category_id: c.category_id || '',
          instructor_name: c.instructor_name || '',
        })
        setChapters(c.chapters || [])
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
      const body = { ...form, price: Number(form.price), original_price: form.original_price ? Number(form.original_price) : undefined, category_id: form.category_id || undefined }
      if (isNew) {
        const { data } = await api.post('/admin/courses', body)
        router.push(`/admin/courses/${data.id}`)
      } else {
        await api.patch(`/admin/courses/${id}`, body)
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
          <Link href="/admin/courses" style={{ fontSize: '13px', color: '#666', textDecoration: 'none' }}>← Danh sách</Link>
          <h1 style={{ marginTop: '4px' }}>{isNew ? 'Thêm khóa học' : 'Chỉnh sửa khóa học'}</h1>
        </div>
      </div>
      <div className="admin-body">
        {error && <div className="alert alert-error">{error}</div>}
        {success && <div className="alert alert-success">{success}</div>}

        <form onSubmit={save}>
          <div className="grid-2" style={{ gap: '20px', alignItems: 'start' }}>
            <div>
              <div className="card" style={{ marginBottom: '20px' }}>
                <h3 style={{ fontWeight: 700, marginBottom: '16px' }}>Thông tin cơ bản</h3>
                <div className="form-group">
                  <label className="form-label">Tiêu đề *</label>
                  <input className="form-input" value={form.title} onChange={set('title')} required />
                </div>
                <div className="form-group">
                  <label className="form-label">Slug (URL)</label>
                  <input className="form-input" value={form.slug} onChange={set('slug')} placeholder="tu-dong-tao-tu-tieu-de" />
                </div>
                <div className="form-group">
                  <label className="form-label">Mô tả ngắn</label>
                  <textarea className="form-input" value={form.short_desc} onChange={set('short_desc')} rows={2} style={{ resize: 'vertical' }} />
                </div>
                <div className="form-group">
                  <label className="form-label">Mô tả chi tiết</label>
                  <textarea className="form-input" value={form.description} onChange={set('description')} rows={6} style={{ resize: 'vertical' }} />
                </div>
                <div className="form-group">
                  <label className="form-label">Tên giảng viên</label>
                  <input className="form-input" value={form.instructor_name} onChange={set('instructor_name')} />
                </div>
              </div>
            </div>

            <div>
              <div className="card" style={{ marginBottom: '20px' }}>
                <h3 style={{ fontWeight: 700, marginBottom: '16px' }}>Cài đặt</h3>
                <div className="form-row">
                  <div className="form-group">
                    <label className="form-label">Giá bán (VND) *</label>
                    <input className="form-input" type="number" value={form.price} onChange={set('price')} required min="0" />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Giá gốc (VND)</label>
                    <input className="form-input" type="number" value={form.original_price} onChange={set('original_price')} min="0" />
                  </div>
                </div>
                <div className="form-group">
                  <label className="form-label">Danh mục</label>
                  <select className="form-input" value={form.category_id} onChange={set('category_id')}>
                    <option value="">-- Chọn danh mục --</option>
                    {categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                  </select>
                </div>
                <div className="form-row">
                  <div className="form-group">
                    <label className="form-label">Cấp độ</label>
                    <select className="form-input" value={form.level} onChange={set('level')}>
                      <option value="beginner">Cơ bản</option>
                      <option value="intermediate">Trung cấp</option>
                      <option value="advanced">Nâng cao</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label className="form-label">Ngôn ngữ</label>
                    <select className="form-input" value={form.language} onChange={set('language')}>
                      <option value="vi">Tiếng Việt</option>
                      <option value="en">English</option>
                    </select>
                  </div>
                </div>
                <div className="form-group">
                  <label className="form-label">URL ảnh bìa</label>
                  <input className="form-input" value={form.thumbnail_url} onChange={set('thumbnail_url')} placeholder="https://..." />
                  {form.thumbnail_url && <img src={form.thumbnail_url} alt="preview" style={{ width: '100%', marginTop: '8px', borderRadius: '6px', aspectRatio: '16/9', objectFit: 'cover' }} />}
                </div>
              </div>

              <button type="submit" className="btn btn-primary btn-full btn-lg" disabled={saving}>
                {saving ? <span className="spinner" /> : isNew ? 'Tạo khóa học' : 'Lưu thay đổi'}
              </button>
            </div>
          </div>
        </form>

        {/* Chapters (only show when editing existing) */}
        {!isNew && (
          <div className="card" style={{ marginTop: '20px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <h3 style={{ fontWeight: 700 }}>Chương học ({chapters.length})</h3>
              <button className="btn btn-primary btn-sm" onClick={async () => {
                const title = prompt('Tên chương:')
                if (!title) return
                try {
                  await api.post(`/admin/courses/${id}/chapters`, { title, order_index: chapters.length })
                  const { data } = await api.get(`/admin/courses/${id}`)
                  setChapters(data.chapters || [])
                } catch (err) { setError(extractError(err)) }
              }}>+ Thêm chương</button>
            </div>
            {chapters.map(ch => (
              <div key={ch.id} style={{ border: '1px solid #eee', borderRadius: '6px', marginBottom: '8px', overflow: 'hidden' }}>
                <div style={{ padding: '10px 14px', background: '#f6f6f6', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontWeight: 600, fontSize: '14px' }}>{ch.title}</span>
                  <div style={{ display: 'flex', gap: '6px' }}>
                    <button className="btn btn-sm btn-ghost" onClick={async () => {
                      const t = prompt('Tên bài học mới:')
                      if (!t) return
                      const vUrl = prompt('URL video (bỏ trống nếu chưa có):') || undefined
                      try {
                        await api.post(`/admin/courses/${id}/chapters/${ch.id}/lessons`, { title: t, order_index: ch.lessons?.length || 0, video_url: vUrl })
                        const { data } = await api.get(`/admin/courses/${id}`)
                        setChapters(data.chapters || [])
                      } catch (err) { setError(extractError(err)) }
                    }}>+ Bài học</button>
                    <button className="btn btn-sm btn-danger" onClick={async () => {
                      if (!confirm(`Xóa chương "${ch.title}"?`)) return
                      try {
                        await api.delete(`/admin/courses/${id}/chapters/${ch.id}`)
                        setChapters(prev => prev.filter(c => c.id !== ch.id))
                      } catch (err) { setError(extractError(err)) }
                    }}>Xóa</button>
                  </div>
                </div>
                {ch.lessons?.map(l => (
                  <div key={l.id} style={{ padding: '8px 14px', display: 'flex', alignItems: 'center', gap: '8px', borderTop: '1px solid #eee', fontSize: '13px' }}>
                    <span>▶</span>
                    <span style={{ flex: 1 }}>{l.title}</span>
                    {l.is_preview && <span className="tag tag-info">Preview</span>}
                    <button className="btn btn-sm btn-danger" onClick={async () => {
                      if (!confirm(`Xóa bài "${l.title}"?`)) return
                      try {
                        await api.delete(`/admin/courses/${id}/chapters/${ch.id}/lessons/${l.id}`)
                        const { data } = await api.get(`/admin/courses/${id}`)
                        setChapters(data.chapters || [])
                      } catch (err) { setError(extractError(err)) }
                    }}>Xóa</button>
                  </div>
                ))}
              </div>
            ))}
          </div>
        )}
      </div>
    </>
  )
}

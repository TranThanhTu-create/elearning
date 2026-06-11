'use client'

import { useState, useEffect } from 'react'
import { api, extractError } from '@/lib/api'
import { formatVnd, formatDate } from '@/lib/utils'
import type { Coupon } from '@/types'

export default function AdminCouponsPage() {
  const [coupons, setCoupons] = useState<Coupon[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ code: '', type: 'percent', value: '', min_order_amount: '', max_uses: '', valid_until: '' })
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  const fetch = async () => {
    setLoading(true)
    try {
      const { data } = await api.get('/admin/coupons?page_size=50')
      setCoupons(data.items || [])
    } catch { setCoupons([]) }
    finally { setLoading(false) }
  }

  useEffect(() => { fetch() }, [])

  const genCode = async () => {
    try {
      const { data } = await api.get('/admin/coupons/generate-code')
      setForm(f => ({ ...f, code: data.code }))
    } catch {}
  }

  const save = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    setError('')
    try {
      await api.post('/admin/coupons', {
        ...form,
        value: Number(form.value),
        min_order_amount: form.min_order_amount ? Number(form.min_order_amount) : undefined,
        max_uses: form.max_uses ? Number(form.max_uses) : undefined,
        valid_until: form.valid_until || undefined,
      })
      setShowForm(false)
      setForm({ code: '', type: 'percent', value: '', min_order_amount: '', max_uses: '', valid_until: '' })
      await fetch()
    } catch (err) {
      setError(extractError(err))
    } finally {
      setSaving(false)
    }
  }

  const deleteCoupon = async (id: string, code: string) => {
    if (!confirm(`Xóa mã "${code}"?`)) return
    try { await api.delete(`/admin/coupons/${id}`); await fetch() }
    catch (err) { setError(extractError(err)) }
  }

  return (
    <>
      <div className="admin-header">
        <h1>Mã giảm giá</h1>
        <button className="btn btn-primary btn-sm" onClick={() => setShowForm(!showForm)}>+ Tạo mã mới</button>
      </div>
      <div className="admin-body">
        {error && <div className="alert alert-error">{error}</div>}

        {showForm && (
          <div className="card" style={{ marginBottom: '20px', border: '2px solid #111' }}>
            <h3 style={{ fontWeight: 700, marginBottom: '16px' }}>Tạo mã giảm giá mới</h3>
            <form onSubmit={save}>
              <div className="form-row">
                <div className="form-group">
                  <label className="form-label">Mã coupon *</label>
                  <div style={{ display: 'flex', gap: '6px' }}>
                    <input className="form-input" value={form.code} onChange={e => setForm(f => ({ ...f, code: e.target.value.toUpperCase() }))} required placeholder="SUMMER30" style={{ flex: 1 }} />
                    <button type="button" className="btn btn-ghost btn-sm" onClick={genCode}>Tạo tự động</button>
                  </div>
                </div>
                <div className="form-group">
                  <label className="form-label">Loại giảm giá</label>
                  <select className="form-input" value={form.type} onChange={e => setForm(f => ({ ...f, type: e.target.value }))}>
                    <option value="percent">Phần trăm (%)</option>
                    <option value="fixed">Số tiền cố định (₫)</option>
                  </select>
                </div>
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label className="form-label">Giá trị {form.type === 'percent' ? '(%)' : '(VND)'} *</label>
                  <input className="form-input" type="number" value={form.value} onChange={e => setForm(f => ({ ...f, value: e.target.value }))} required min="1" max={form.type === 'percent' ? '100' : undefined} />
                </div>
                <div className="form-group">
                  <label className="form-label">Đơn tối thiểu (VND)</label>
                  <input className="form-input" type="number" value={form.min_order_amount} onChange={e => setForm(f => ({ ...f, min_order_amount: e.target.value }))} />
                </div>
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label className="form-label">Giới hạn lượt dùng</label>
                  <input className="form-input" type="number" value={form.max_uses} onChange={e => setForm(f => ({ ...f, max_uses: e.target.value }))} placeholder="Không giới hạn" />
                </div>
                <div className="form-group">
                  <label className="form-label">Ngày hết hạn</label>
                  <input className="form-input" type="date" value={form.valid_until} onChange={e => setForm(f => ({ ...f, valid_until: e.target.value }))} />
                </div>
              </div>
              <div style={{ display: 'flex', gap: '8px' }}>
                <button type="submit" className="btn btn-primary" disabled={saving}>{saving ? <span className="spinner" /> : 'Tạo mã'}</button>
                <button type="button" className="btn btn-ghost" onClick={() => setShowForm(false)}>Hủy</button>
              </div>
            </form>
          </div>
        )}

        {loading ? <div className="skeleton" style={{ height: '300px' }} /> : (
          <div className="card" style={{ padding: 0 }}>
            <div className="table-wrap">
              <table>
                <thead><tr><th>Mã</th><th>Loại & Giá trị</th><th>Đã dùng</th><th>Đơn tối thiểu</th><th>Hạn dùng</th><th>Trạng thái</th><th>Thao tác</th></tr></thead>
                <tbody>
                  {coupons.map(c => (
                    <tr key={c.id}>
                      <td><strong style={{ fontFamily: 'monospace', letterSpacing: '1px' }}>{c.code}</strong></td>
                      <td>{c.type === 'percent' ? `${c.value}%` : formatVnd(c.value)}</td>
                      <td>{c.used_count}{c.max_uses ? `/${c.max_uses}` : ''}</td>
                      <td>{c.min_order_amount ? formatVnd(c.min_order_amount) : '—'}</td>
                      <td style={{ fontSize: '12px' }}>{c.valid_until ? formatDate(c.valid_until) : 'Không giới hạn'}</td>
                      <td><span className={`tag ${c.status === 'active' ? 'tag-success' : c.status === 'expired' ? 'tag-danger' : 'tag-default'}`}>{c.status_label || c.status}</span></td>
                      <td><button className="btn btn-danger btn-sm" onClick={() => deleteCoupon(c.id, c.code)}>Xóa</button></td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {coupons.length === 0 && <div className="empty-state">Chưa có mã giảm giá</div>}
            </div>
          </div>
        )}
      </div>
    </>
  )
}

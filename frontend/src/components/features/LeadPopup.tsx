'use client'

import { useState, useEffect } from 'react'
import { api, extractError } from '@/lib/api'

export default function LeadPopup() {
  const [visible, setVisible] = useState(false)
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [phone, setPhone] = useState('')
  const [loading, setLoading] = useState(false)
  const [done, setDone] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (typeof window === 'undefined') return
    const dismissed = sessionStorage.getItem('lead_popup_dismissed')
    if (dismissed) return
    const t = setTimeout(() => setVisible(true), 8000)
    return () => clearTimeout(t)
  }, [])

  const dismiss = () => {
    sessionStorage.setItem('lead_popup_dismissed', '1')
    setVisible(false)
  }

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      const params = new URLSearchParams(window.location.search)
      await api.post('/leads', {
        name,
        email,
        phone,
        utm_source: params.get('utm_source') || undefined,
        utm_medium: params.get('utm_medium') || undefined,
        utm_campaign: params.get('utm_campaign') || undefined,
        page_url: window.location.href,
      })
      setDone(true)
      setTimeout(dismiss, 3000)
    } catch (err) {
      setError(extractError(err))
    } finally {
      setLoading(false)
    }
  }

  if (!visible) return null

  return (
    <div className="modal-overlay" style={{ zIndex: 9999 }} onClick={(e) => { if (e.target === e.currentTarget) dismiss() }}>
      <div className="modal-box" style={{ maxWidth: '400px' }}>
        <div className="modal-header">
          <h3>Nhận tài liệu miễn phí</h3>
          <button className="modal-close" onClick={dismiss}>×</button>
        </div>
        <div className="modal-body">
          {done ? (
            <div className="alert alert-success">Đăng ký thành công! Chúng tôi sẽ liên hệ sớm.</div>
          ) : (
            <form onSubmit={submit}>
              <p style={{ fontSize: '14px', color: '#666', marginBottom: '16px' }}>
                Để lại thông tin để nhận tài liệu học tập và ưu đãi độc quyền.
              </p>
              {error && <div className="alert alert-error">{error}</div>}
              <div className="form-group">
                <label className="form-label">Họ và tên</label>
                <input className="form-input" value={name} onChange={e => setName(e.target.value)} required placeholder="Nguyễn Văn A" />
              </div>
              <div className="form-group">
                <label className="form-label">Email</label>
                <input className="form-input" type="email" value={email} onChange={e => setEmail(e.target.value)} required placeholder="email@example.com" />
              </div>
              <div className="form-group">
                <label className="form-label">Số điện thoại</label>
                <input className="form-input" value={phone} onChange={e => setPhone(e.target.value)} placeholder="0901234567" />
              </div>
              <button type="submit" className="btn btn-primary btn-full btn-lg" disabled={loading}>
                {loading ? <span className="spinner" /> : 'Nhận ngay'}
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  )
}

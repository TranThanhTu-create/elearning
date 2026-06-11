'use client'

import { useState } from 'react'
import { api } from '@/lib/api'

const ZALO_GROUP_URL = 'https://zalo.me/g/tumarketing' // CẬP NHẬT LINK ZALO THẬT

export default function LandingForm() {
  const [form, setForm] = useState({ name: '', phone: '', email: '' })
  const [loading, setLoading] = useState(false)
  const [done, setDone] = useState(false)
  const [error, setError] = useState('')

  const set = (k: string) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm(f => ({ ...f, [k]: e.target.value }))

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!form.name.trim() || !form.phone.trim()) {
      setError('Vui lòng nhập họ tên và số điện thoại')
      return
    }
    setLoading(true)
    setError('')
    try {
      await api.post('/leads', {
        name: form.name.trim(),
        phone: form.phone.trim(),
        email: form.email.trim() || undefined,
        source: 'landing_page',
      })
      setDone(true)
    } catch {
      // save lead failed silently — still show success
      setDone(true)
    } finally {
      setLoading(false)
    }
  }

  if (done) {
    return (
      <div style={{ textAlign: 'center', padding: '40px 20px' }}>
        <div style={{ fontSize: '56px', marginBottom: '16px' }}>🎉</div>
        <h3 style={{ fontSize: '24px', fontWeight: 800, color: 'var(--neon)', marginBottom: '12px' }}>
          Đăng ký thành công!
        </h3>
        <p style={{ color: 'var(--text-muted)', fontSize: '16px', marginBottom: '28px', lineHeight: 1.7 }}>
          Cảm ơn <strong style={{ color: 'var(--text)' }}>{form.name}</strong>! Tú Marketing đã nhận thông tin của bạn.<br />
          Tham gia nhóm Zalo để nhận link buổi training và tài liệu miễn phí nhé!
        </p>
        <a
          href={ZALO_GROUP_URL}
          target="_blank"
          rel="noopener noreferrer"
          className="btn btn-primary btn-xl"
          style={{ display: 'inline-flex', gap: '10px', fontSize: '17px' }}
        >
          <span>💬</span> Tham gia nhóm Zalo ngay →
        </a>
        <p style={{ fontSize: '13px', color: 'var(--text-dim)', marginTop: '16px' }}>
          Hoặc tìm nhóm Zalo: <strong style={{ color: 'var(--neon)' }}>Tú Marketing — AI Agent</strong>
        </p>
      </div>
    )
  }

  return (
    <form onSubmit={submit}>
      {error && (
        <div className="alert alert-error" style={{ marginBottom: '16px' }}>{error}</div>
      )}
      <div className="form-group">
        <label className="form-label">Họ và tên *</label>
        <input
          className="form-input"
          placeholder="Nguyễn Văn A"
          value={form.name}
          onChange={set('name')}
          required
          style={{ fontSize: '15px', padding: '13px 16px' }}
        />
      </div>
      <div className="form-group">
        <label className="form-label">Số điện thoại *</label>
        <input
          className="form-input"
          placeholder="09xx xxx xxx"
          value={form.phone}
          onChange={set('phone')}
          type="tel"
          required
          style={{ fontSize: '15px', padding: '13px 16px' }}
        />
      </div>
      <div className="form-group" style={{ marginBottom: '24px' }}>
        <label className="form-label">Email <span style={{ color: 'var(--text-dim)', fontWeight: 400 }}>(tùy chọn)</span></label>
        <input
          className="form-input"
          placeholder="email@example.com"
          value={form.email}
          onChange={set('email')}
          type="email"
          style={{ fontSize: '15px', padding: '13px 16px' }}
        />
      </div>
      <button
        type="submit"
        className="btn btn-primary btn-full"
        disabled={loading}
        style={{ fontSize: '17px', padding: '16px', borderRadius: '12px', fontWeight: 800, letterSpacing: '0.3px' }}
      >
        {loading ? <span className="spinner" /> : '🔥 ĐĂNG KÝ THAM GIA MIỄN PHÍ →'}
      </button>
      <p style={{ textAlign: 'center', fontSize: '13px', color: 'var(--text-dim)', marginTop: '12px' }}>
        🔒 100% miễn phí · Không spam · Hủy bất kỳ lúc nào
      </p>
    </form>
  )
}

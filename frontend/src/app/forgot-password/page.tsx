'use client'

import { useState } from 'react'
import Link from 'next/link'
import { api, extractError } from '@/lib/api'

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [sent, setSent] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      await api.post('/auth/forgot-password', { email })
      setSent(true)
    } catch (err) {
      setError(extractError(err))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#f6f6f6', padding: '24px' }}>
      <div style={{ width: '100%', maxWidth: '400px' }}>
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <Link href="/" style={{ fontSize: '24px', fontWeight: 800, color: '#111', textDecoration: 'none' }}>EduVietPro</Link>
        </div>
        <div className="card-dark" style={{ padding: '32px' }}>
          <h1 style={{ fontSize: '20px', fontWeight: 800, marginBottom: '8px' }}>Quên mật khẩu</h1>
          {sent ? (
            <div>
              <div className="alert alert-success">Email đặt lại mật khẩu đã được gửi. Vui lòng kiểm tra hộp thư.</div>
              <Link href="/login" className="btn btn-ghost btn-full" style={{ marginTop: '8px' }}>Quay lại đăng nhập</Link>
            </div>
          ) : (
            <>
              <p style={{ color: '#666', fontSize: '14px', marginBottom: '20px' }}>Nhập email đăng ký để nhận hướng dẫn đặt lại mật khẩu.</p>
              {error && <div className="alert alert-error">{error}</div>}
              <form onSubmit={handleSubmit}>
                <div className="form-group">
                  <label className="form-label">Email</label>
                  <input className="form-input" type="email" value={email} onChange={e => setEmail(e.target.value)} required placeholder="email@example.com" autoFocus />
                </div>
                <button type="submit" className="btn btn-primary btn-full" disabled={loading}>
                  {loading ? <span className="spinner" /> : 'Gửi email'}
                </button>
              </form>
            </>
          )}
        </div>
        <p style={{ textAlign: 'center', marginTop: '16px', fontSize: '14px' }}>
          <Link href="/login" style={{ color: '#111' }}>← Quay lại đăng nhập</Link>
        </p>
      </div>
    </div>
  )
}

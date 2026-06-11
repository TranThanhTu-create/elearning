'use client'

import { useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/lib/auth'
import { extractError } from '@/lib/api'

export default function LoginPage() {
  const [identifier, setIdentifier] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(identifier, password)
      router.push('/dashboard')
    } catch (err) {
      setError(extractError(err))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{
      minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center',
      background: 'radial-gradient(ellipse 80% 60% at 50% 0%, rgba(0,212,255,0.10) 0%, transparent 60%), var(--bg)',
      padding: '24px', position: 'relative', overflow: 'hidden',
    }}>
      {/* grid bg */}
      <div style={{ position: 'fixed', inset: 0, backgroundImage: 'linear-gradient(rgba(0,212,255,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(0,212,255,0.03) 1px, transparent 1px)', backgroundSize: '60px 60px', pointerEvents: 'none' }} />

      <div style={{ width: '100%', maxWidth: '420px', position: 'relative' }}>
        {/* Logo */}
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <Link href="/" style={{ display: 'inline-block', fontSize: '26px', fontWeight: 900, background: 'linear-gradient(135deg, #00d4ff, #7b2fff)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text', textDecoration: 'none', letterSpacing: '-0.5px' }}>
            Tú Marketing
          </Link>
          <p style={{ color: 'var(--text-muted)', marginTop: '8px', fontSize: '15px' }}>Đăng nhập để tiếp tục học</p>
        </div>

        {/* Card */}
        <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border-bright)', borderRadius: '20px', padding: '36px', boxShadow: '0 20px 60px rgba(0,0,0,0.5), 0 0 40px rgba(0,212,255,0.05)' }}>
          <h1 style={{ fontSize: '20px', fontWeight: 800, color: 'var(--text)', marginBottom: '24px' }}>Đăng nhập</h1>

          {error && <div className="alert alert-error">{error}</div>}

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label">Email hoặc tên đăng nhập</label>
              <input
                className="form-input"
                type="text"
                value={identifier}
                onChange={e => setIdentifier(e.target.value)}
                required
                autoFocus
                placeholder="email@example.com"
              />
            </div>
            <div className="form-group">
              <label className="form-label" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span>Mật khẩu</span>
                <Link href="/forgot-password" style={{ fontWeight: 500, color: 'var(--neon)', fontSize: '12px', textDecoration: 'none' }}>Quên mật khẩu?</Link>
              </label>
              <input
                className="form-input"
                type="password"
                value={password}
                onChange={e => setPassword(e.target.value)}
                required
                placeholder="••••••••"
              />
            </div>
            <button type="submit" className="btn btn-primary btn-full btn-lg" disabled={loading} style={{ marginTop: '8px' }}>
              {loading ? <span className="spinner" /> : 'Đăng nhập →'}
            </button>
          </form>

          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', margin: '20px 0', color: 'var(--text-dim)', fontSize: '12px' }}>
            <div style={{ flex: 1, height: '1px', background: 'var(--border)' }} />
            <span>hoặc</span>
            <div style={{ flex: 1, height: '1px', background: 'var(--border)' }} />
          </div>

          <Link href="/register" className="btn btn-ghost btn-full" style={{ textAlign: 'center', display: 'block' }}>
            Tạo tài khoản mới miễn phí
          </Link>
        </div>

        <p style={{ textAlign: 'center', marginTop: '20px', fontSize: '14px', color: 'var(--text-dim)' }}>
          Chưa có tài khoản?{' '}
          <Link href="/register" style={{ color: 'var(--neon)', fontWeight: 700, textDecoration: 'none' }}>Đăng ký ngay</Link>
        </p>
      </div>
    </div>
  )
}

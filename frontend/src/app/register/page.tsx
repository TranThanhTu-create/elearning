'use client'

import { useState, Suspense } from 'react'
import Link from 'next/link'
import { useRouter, useSearchParams } from 'next/navigation'
import { useAuth } from '@/lib/auth'
import { api, extractError } from '@/lib/api'

function RegisterForm() {
  const [form, setForm] = useState({ name: '', email: '', password: '', password2: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const router = useRouter()
  const params = useSearchParams()
  const ref = params.get('ref') || undefined

  const set = (k: string) => (e: React.ChangeEvent<HTMLInputElement>) => setForm(f => ({ ...f, [k]: e.target.value }))

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    if (form.password !== form.password2) { setError('Mật khẩu xác nhận không khớp'); return }
    if (form.password.length < 6) { setError('Mật khẩu phải ít nhất 6 ký tự'); return }
    setLoading(true)
    try {
      await api.post('/auth/register', {
        name: form.name,
        email: form.email,
        password: form.password,
        ref_code: ref,
      })
      await login(form.email, form.password)
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
      background: 'radial-gradient(ellipse 80% 60% at 50% 0%, rgba(123,47,255,0.10) 0%, transparent 60%), var(--bg)',
      padding: '24px', position: 'relative', overflow: 'hidden',
    }}>
      <div style={{ position: 'fixed', inset: 0, backgroundImage: 'linear-gradient(rgba(0,212,255,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(0,212,255,0.03) 1px, transparent 1px)', backgroundSize: '60px 60px', pointerEvents: 'none' }} />

      <div style={{ width: '100%', maxWidth: '460px', position: 'relative' }}>
        {/* Logo */}
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <Link href="/" style={{ display: 'inline-block', fontSize: '26px', fontWeight: 900, background: 'linear-gradient(135deg, #00d4ff, #7b2fff)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text', textDecoration: 'none', letterSpacing: '-0.5px' }}>
            Tú Marketing
          </Link>
          <p style={{ color: 'var(--text-muted)', marginTop: '8px', fontSize: '15px' }}>Tạo tài khoản miễn phí ngay hôm nay</p>
        </div>

        {/* Card */}
        <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border-bright)', borderRadius: '20px', padding: '36px', boxShadow: '0 20px 60px rgba(0,0,0,0.5), 0 0 40px rgba(123,47,255,0.05)' }}>
          <h1 style={{ fontSize: '20px', fontWeight: 800, color: 'var(--text)', marginBottom: '24px' }}>Đăng ký tài khoản</h1>

          {ref && <div className="alert alert-info" style={{ marginBottom: '16px' }}>🎁 Bạn được giới thiệu qua link affiliate. Người giới thiệu sẽ nhận hoa hồng khi bạn mua khóa học.</div>}
          {error && <div className="alert alert-error">{error}</div>}

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label">Họ và tên</label>
              <input className="form-input" value={form.name} onChange={set('name')} required placeholder="Nguyễn Văn A" />
            </div>
            <div className="form-group">
              <label className="form-label">Email</label>
              <input className="form-input" type="email" value={form.email} onChange={set('email')} required placeholder="email@example.com" />
            </div>
            <div className="form-row">
              <div className="form-group">
                <label className="form-label">Mật khẩu</label>
                <input className="form-input" type="password" value={form.password} onChange={set('password')} required placeholder="••••••••" minLength={6} />
              </div>
              <div className="form-group">
                <label className="form-label">Xác nhận mật khẩu</label>
                <input className="form-input" type="password" value={form.password2} onChange={set('password2')} required placeholder="••••••••" />
              </div>
            </div>
            <button type="submit" className="btn btn-primary btn-full btn-lg" disabled={loading} style={{ marginTop: '8px' }}>
              {loading ? <span className="spinner" /> : 'Tạo tài khoản →'}
            </button>
            <p style={{ fontSize: '12px', color: 'var(--text-dim)', marginTop: '12px', textAlign: 'center', lineHeight: 1.7 }}>
              Bằng cách đăng ký, bạn đồng ý với{' '}
              <Link href="/dieu-khoan" style={{ color: 'var(--neon)', textDecoration: 'none' }}>Điều khoản</Link>
              {' '}và{' '}
              <Link href="/chinh-sach-bao-mat" style={{ color: 'var(--neon)', textDecoration: 'none' }}>Chính sách bảo mật</Link>
            </p>
          </form>
        </div>

        <p style={{ textAlign: 'center', marginTop: '20px', fontSize: '14px', color: 'var(--text-dim)' }}>
          Đã có tài khoản?{' '}
          <Link href="/login" style={{ color: 'var(--neon)', fontWeight: 700, textDecoration: 'none' }}>Đăng nhập</Link>
        </p>
      </div>
    </div>
  )
}

export default function RegisterPage() {
  return <Suspense><RegisterForm /></Suspense>
}

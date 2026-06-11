'use client'

import { Suspense, useEffect, useState } from 'react'
import { useSearchParams, useRouter } from 'next/navigation'
import Link from 'next/link'
import Navbar from '@/components/layout/Navbar'
import Footer from '@/components/layout/Footer'
import { api, extractError } from '@/lib/api'

type State = 'loading' | 'success' | 'error' | 'no-token'

function VerifyEmailContent() {
  const params = useSearchParams()
  const router = useRouter()
  const token = params.get('token')

  const [state, setState] = useState<State>(token ? 'loading' : 'no-token')
  const [errorMsg, setErrorMsg] = useState('')

  useEffect(() => {
    if (!token) return

    api.post('/auth/verify-email', null, { params: { token } })
      .then(() => {
        setState('success')
        setTimeout(() => router.push('/login'), 3000)
      })
      .catch((err) => {
        setErrorMsg(extractError(err))
        setState('error')
      })
  }, [token, router])

  return (
    <div className="card" style={{ textAlign: 'center', padding: '48px 32px' }}>
      {state === 'loading' && (
        <>
          <div className="spinner" style={{ width: '40px', height: '40px', margin: '0 auto 16px' }} />
          <h1 style={{ fontSize: '20px', fontWeight: 800, marginBottom: '8px' }}>Đang xác thực...</h1>
          <p style={{ color: '#666' }}>Vui lòng chờ trong giây lát.</p>
        </>
      )}

      {state === 'success' && (
        <>
          <div style={{ fontSize: '56px', marginBottom: '16px' }}>✅</div>
          <h1 style={{ fontSize: '22px', fontWeight: 800, marginBottom: '8px' }}>Xác thực thành công!</h1>
          <p style={{ color: '#555', marginBottom: '24px', lineHeight: 1.6 }}>
            Email của bạn đã được xác thực. Bạn sẽ được chuyển đến trang đăng nhập trong giây lát...
          </p>
          <Link href="/login" className="btn btn-primary">Đăng nhập ngay</Link>
        </>
      )}

      {state === 'error' && (
        <>
          <div style={{ fontSize: '56px', marginBottom: '16px' }}>❌</div>
          <h1 style={{ fontSize: '22px', fontWeight: 800, marginBottom: '8px' }}>Xác thực thất bại</h1>
          <p style={{ color: '#555', marginBottom: '24px', lineHeight: 1.6 }}>
            {errorMsg || 'Link xác thực không hợp lệ hoặc đã hết hạn.'}
          </p>
          <div style={{ display: 'flex', gap: '12px', justifyContent: 'center', flexWrap: 'wrap' }}>
            <Link href="/login" className="btn btn-ghost">Đăng nhập</Link>
            <ResendButton />
          </div>
        </>
      )}

      {state === 'no-token' && (
        <>
          <div style={{ fontSize: '56px', marginBottom: '16px' }}>📧</div>
          <h1 style={{ fontSize: '22px', fontWeight: 800, marginBottom: '8px' }}>Kiểm tra email</h1>
          <p style={{ color: '#555', marginBottom: '24px', lineHeight: 1.6 }}>
            Chúng tôi đã gửi email xác thực đến địa chỉ bạn đăng ký.
            Hãy click vào link trong email để xác thực tài khoản.
          </p>
          <p style={{ color: '#888', fontSize: '13px', marginBottom: '24px' }}>
            Không thấy email? Kiểm tra thư mục spam hoặc gửi lại bên dưới.
          </p>
          <div style={{ display: 'flex', gap: '12px', justifyContent: 'center', flexWrap: 'wrap' }}>
            <Link href="/login" className="btn btn-ghost">Đăng nhập</Link>
            <ResendButton />
          </div>
        </>
      )}
    </div>
  )
}

function ResendButton() {
  const [sent, setSent] = useState(false)
  const [loading, setLoading] = useState(false)

  const resend = async () => {
    setLoading(true)
    try {
      await api.post('/auth/resend-verification')
      setSent(true)
    } catch {
      // user may not be logged in; silently ignore
    } finally {
      setLoading(false)
    }
  }

  if (sent) return <span style={{ color: '#27ae60', fontSize: '14px', fontWeight: 600 }}>Đã gửi lại!</span>

  return (
    <button className="btn btn-primary" onClick={resend} disabled={loading}>
      {loading ? <span className="spinner" /> : 'Gửi lại email'}
    </button>
  )
}

export default function VerifyEmailPage() {
  return (
    <>
      <Navbar />
      <main style={{ flex: 1 }}>
        <div className="section">
          <div className="container" style={{ maxWidth: '480px' }}>
            <Suspense fallback={
              <div className="card" style={{ textAlign: 'center', padding: '48px 32px' }}>
                <div className="spinner" style={{ width: '40px', height: '40px', margin: '0 auto 16px' }} />
                <p style={{ color: '#666' }}>Đang tải...</p>
              </div>
            }>
              <VerifyEmailContent />
            </Suspense>
          </div>
        </div>
      </main>
      <Footer />
    </>
  )
}

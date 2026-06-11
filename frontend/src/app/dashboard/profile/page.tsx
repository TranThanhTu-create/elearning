'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import Navbar from '@/components/layout/Navbar'
import Footer from '@/components/layout/Footer'
import { api, extractError } from '@/lib/api'
import { useAuth } from '@/lib/auth'

export default function ProfilePage() {
  const { user, refreshUser } = useAuth()
  const [form, setForm] = useState({ name: '', phone: '' })
  const [pwForm, setPwForm] = useState({ old_password: '', new_password: '', confirm: '' })
  const [loading, setSaving] = useState(false)
  const [pwLoading, setPwLoading] = useState(false)
  const [success, setSuccess] = useState('')
  const [error, setError] = useState('')
  const [pwError, setPwError] = useState('')
  const [pwSuccess, setPwSuccess] = useState('')

  useEffect(() => {
    if (user) setForm({ name: user.name || '', phone: user.phone || '' })
  }, [user])

  const set = (k: string) => (e: React.ChangeEvent<HTMLInputElement>) => setForm(f => ({ ...f, [k]: e.target.value }))
  const setPw = (k: string) => (e: React.ChangeEvent<HTMLInputElement>) => setPwForm(f => ({ ...f, [k]: e.target.value }))

  const saveProfile = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    setError('')
    setSuccess('')
    try {
      await api.put('/dashboard/profile', form)
      await refreshUser()
      setSuccess('Cập nhật hồ sơ thành công!')
    } catch (err) {
      setError(extractError(err))
    } finally {
      setSaving(false)
    }
  }

  const changePassword = async (e: React.FormEvent) => {
    e.preventDefault()
    if (pwForm.new_password !== pwForm.confirm) { setPwError('Mật khẩu mới không khớp'); return }
    setPwLoading(true)
    setPwError('')
    setPwSuccess('')
    try {
      await api.post('/auth/change-password', { current_password: pwForm.old_password, new_password: pwForm.new_password })
      setPwSuccess('Đổi mật khẩu thành công!')
      setPwForm({ old_password: '', new_password: '', confirm: '' })
    } catch (err) {
      setPwError(extractError(err))
    } finally {
      setPwLoading(false)
    }
  }

  return (
    <>
      <Navbar />
      <main style={{ flex: 1 }}>
        <div style={{ background: '#f6f6f6', borderBottom: '1px solid #eee', padding: '24px 0' }}>
          <div className="container">
            <h1 style={{ fontSize: '22px', fontWeight: 800 }}>Hồ sơ cá nhân</h1>
          </div>
        </div>
        <div className="section-sm">
          <div className="container" style={{ maxWidth: '640px' }}>
            <div className="tabs" style={{ marginBottom: '24px' }}>
              <Link href="/dashboard" className="tab">Khóa học</Link>
              <Link href="/dashboard/profile" className="tab active">Hồ sơ</Link>
              <Link href="/dashboard/affiliate" className="tab">Affiliate</Link>
            </div>

            {/* Profile form */}
            <div className="card" style={{ marginBottom: '20px' }}>
              <h2 style={{ fontSize: '17px', fontWeight: 700, marginBottom: '20px' }}>Thông tin cá nhân</h2>
              {success && <div className="alert alert-success">{success}</div>}
              {error && <div className="alert alert-error">{error}</div>}
              <form onSubmit={saveProfile}>
                <div className="form-group">
                  <label className="form-label">Họ và tên</label>
                  <input className="form-input" value={form.name} onChange={set('name')} required />
                </div>
                <div className="form-group">
                  <label className="form-label">Số điện thoại</label>
                  <input className="form-input" value={form.phone} onChange={set('phone')} />
                </div>
                <div className="form-group">
                  <label className="form-label">Email</label>
                  <input className="form-input" value={user?.email || ''} disabled />
                </div>
                <button type="submit" className="btn btn-primary" disabled={loading}>
                  {loading ? <span className="spinner" /> : 'Lưu thay đổi'}
                </button>
              </form>
            </div>

            {/* Password form */}
            <div className="card">
              <h2 style={{ fontSize: '17px', fontWeight: 700, marginBottom: '20px' }}>Đổi mật khẩu</h2>
              {pwSuccess && <div className="alert alert-success">{pwSuccess}</div>}
              {pwError && <div className="alert alert-error">{pwError}</div>}
              <form onSubmit={changePassword}>
                <div className="form-group">
                  <label className="form-label">Mật khẩu hiện tại</label>
                  <input className="form-input" type="password" value={pwForm.old_password} onChange={setPw('old_password')} required />
                </div>
                <div className="form-row">
                  <div className="form-group">
                    <label className="form-label">Mật khẩu mới</label>
                    <input className="form-input" type="password" value={pwForm.new_password} onChange={setPw('new_password')} required minLength={6} />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Xác nhận mật khẩu</label>
                    <input className="form-input" type="password" value={pwForm.confirm} onChange={setPw('confirm')} required />
                  </div>
                </div>
                <button type="submit" className="btn btn-ghost" disabled={pwLoading}>
                  {pwLoading ? <span className="spinner" /> : 'Đổi mật khẩu'}
                </button>
              </form>
            </div>
          </div>
        </div>
      </main>
      <Footer />
    </>
  )
}

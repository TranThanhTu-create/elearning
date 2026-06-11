'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import Navbar from '@/components/layout/Navbar'
import Footer from '@/components/layout/Footer'
import { api, extractError } from '@/lib/api'
import { formatVnd, formatDate, getStatusTag } from '@/lib/utils'
import type { AffiliateStats, Commission, WithdrawalRequest } from '@/types'

export default function AffiliateDashboardPage() {
  const [stats, setStats] = useState<AffiliateStats | null>(null)
  const [commissions, setCommissions] = useState<Commission[]>([])
  const [withdrawals, setWithdrawals] = useState<WithdrawalRequest[]>([])
  const [loading, setLoading] = useState(true)
  const [copied, setCopied] = useState(false)
  const [showWithdrawForm, setShowWithdrawForm] = useState(false)
  const [wForm, setWForm] = useState({ amount: '', bank_name: '', bank_account: '', account_name: '' })
  const [wLoading, setWLoading] = useState(false)
  const [wError, setWError] = useState('')
  const [wSuccess, setWSuccess] = useState('')

  useEffect(() => {
    Promise.all([
      api.get('/affiliate/stats'),
      api.get('/affiliate/commissions?page_size=20'),
      api.get('/affiliate/withdrawals'),
    ]).then(([s, c, w]) => {
      setStats(s.data)
      setCommissions(c.data.items || [])
      setWithdrawals(w.data || [])
    }).catch(() => {}).finally(() => setLoading(false))
  }, [])

  const copyLink = () => {
    if (!stats?.ref_link) return
    navigator.clipboard.writeText(stats.ref_link).then(() => { setCopied(true); setTimeout(() => setCopied(false), 2000) }).catch(() => {})
  }

  const requestWithdrawal = async (e: React.FormEvent) => {
    e.preventDefault()
    setWLoading(true)
    setWError('')
    try {
      await api.post('/affiliate/withdrawals', {
        amount: Number(wForm.amount.replace(/\D/g, '')),
        bank_name: wForm.bank_name,
        bank_account: wForm.bank_account,
        account_name: wForm.account_name,
      })
      setWSuccess('Đã gửi yêu cầu rút tiền thành công!')
      setShowWithdrawForm(false)
      const wRes = await api.get('/affiliate/withdrawals')
      setWithdrawals(wRes.data || [])
    } catch (err) {
      setWError(extractError(err))
    } finally {
      setWLoading(false)
    }
  }

  if (loading) return (
    <>
      <Navbar />
      <div className="container section">
        <div className="metric-grid">
          {Array.from({ length: 4 }).map((_, i) => <div key={i} className="skeleton" style={{ height: '90px' }} />)}
        </div>
      </div>
      <Footer />
    </>
  )

  return (
    <>
      <Navbar />
      <main style={{ flex: 1 }}>
        <div style={{ background: '#f6f6f6', borderBottom: '1px solid #eee', padding: '24px 0' }}>
          <div className="container">
            <h1 style={{ fontSize: '22px', fontWeight: 800 }}>Affiliate Dashboard</h1>
            <p style={{ color: '#666', marginTop: '4px' }}>Kiếm hoa hồng 40% mỗi đơn hàng thành công</p>
          </div>
        </div>

        <div className="section-sm">
          <div className="container">
            <div className="tabs" style={{ marginBottom: '24px' }}>
              <Link href="/dashboard" className="tab">Khóa học</Link>
              <Link href="/dashboard/profile" className="tab">Hồ sơ</Link>
              <Link href="/dashboard/affiliate" className="tab active">Affiliate</Link>
            </div>

            {/* Ref link */}
            {stats && (
              <div className="card-dark" style={{ marginBottom: '20px' }}>
                <h3 style={{ fontWeight: 700, marginBottom: '12px' }}>Link giới thiệu của bạn</h3>
                <div style={{ display: 'flex', gap: '8px' }}>
                  <input className="form-input" value={stats.ref_link} readOnly style={{ flex: 1, background: '#f6f6f6' }} />
                  <button className="btn btn-primary" onClick={copyLink}>{copied ? '✓ Đã copy' : 'Copy link'}</button>
                </div>
                <p style={{ fontSize: '13px', color: '#666', marginTop: '8px' }}>
                  Mã ref: <strong>{stats.ref_code}</strong> · Bạn nhận 40% hoa hồng cho mỗi đơn hàng qua link này
                </p>
              </div>
            )}

            {/* Stats */}
            {stats && (
              <div className="metric-grid" style={{ marginBottom: '24px' }}>
                {[
                  { label: 'Tổng hoa hồng', value: stats.total_commission_fmt },
                  { label: 'Đã thanh toán', value: stats.paid_commission_fmt },
                  { label: 'Chờ rút', value: stats.pending_commission_fmt },
                  { label: 'Tỷ lệ chuyển đổi', value: stats.conversion_rate_fmt },
                ].map(m => (
                  <div key={m.label} className="metric-card">
                    <div className="metric-label">{m.label}</div>
                    <div className="metric-value" style={{ fontSize: '20px' }}>{m.value}</div>
                  </div>
                ))}
              </div>
            )}

            {/* Commissions */}
            <div className="card" style={{ marginBottom: '20px' }}>
              <h3 style={{ fontWeight: 700, marginBottom: '16px' }}>Lịch sử hoa hồng</h3>
              {commissions.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '32px', color: '#999' }}>Chưa có hoa hồng nào</div>
              ) : (
                <div className="table-wrap">
                  <table>
                    <thead><tr><th>Khóa học</th><th>Đơn hàng</th><th>Hoa hồng</th><th>Trạng thái</th><th>Ngày</th></tr></thead>
                    <tbody>
                      {commissions.map(c => (
                        <tr key={c.id}>
                          <td>{c.course_title}</td>
                          <td><span style={{ fontSize: '12px', fontFamily: 'monospace' }}>{c.order_code}</span></td>
                          <td><strong>{c.commission_amount_fmt}</strong></td>
                          <td><span className={`tag ${getStatusTag(c.status)}`}>{c.status_label}</span></td>
                          <td style={{ fontSize: '13px', color: '#888' }}>{formatDate(c.created_at)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>

            {/* Withdrawals */}
            <div className="card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                <h3 style={{ fontWeight: 700 }}>Rút tiền</h3>
                <button className="btn btn-primary btn-sm" onClick={() => setShowWithdrawForm(!showWithdrawForm)}>+ Yêu cầu rút</button>
              </div>

              {wSuccess && <div className="alert alert-success">{wSuccess}</div>}

              {showWithdrawForm && (
                <form onSubmit={requestWithdrawal} style={{ background: '#f6f6f6', padding: '16px', borderRadius: '8px', marginBottom: '16px' }}>
                  {wError && <div className="alert alert-error">{wError}</div>}
                  <div className="form-row">
                    <div className="form-group">
                      <label className="form-label">Số tiền (tối thiểu 500.000 ₫)</label>
                      <input className="form-input" value={wForm.amount} onChange={e => setWForm(f => ({ ...f, amount: e.target.value }))} required placeholder="500000" type="number" min="500000" />
                    </div>
                    <div className="form-group">
                      <label className="form-label">Ngân hàng</label>
                      <input className="form-input" value={wForm.bank_name} onChange={e => setWForm(f => ({ ...f, bank_name: e.target.value }))} required placeholder="Vietcombank" />
                    </div>
                  </div>
                  <div className="form-row">
                    <div className="form-group">
                      <label className="form-label">Số tài khoản</label>
                      <input className="form-input" value={wForm.bank_account} onChange={e => setWForm(f => ({ ...f, bank_account: e.target.value }))} required />
                    </div>
                    <div className="form-group">
                      <label className="form-label">Tên chủ tài khoản</label>
                      <input className="form-input" value={wForm.account_name} onChange={e => setWForm(f => ({ ...f, account_name: e.target.value }))} required />
                    </div>
                  </div>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <button type="submit" className="btn btn-primary" disabled={wLoading}>{wLoading ? <span className="spinner" /> : 'Gửi yêu cầu'}</button>
                    <button type="button" className="btn btn-ghost" onClick={() => setShowWithdrawForm(false)}>Hủy</button>
                  </div>
                </form>
              )}

              {withdrawals.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '24px', color: '#999' }}>Chưa có yêu cầu rút tiền</div>
              ) : (
                <div className="table-wrap">
                  <table>
                    <thead><tr><th>Số tiền</th><th>Ngân hàng</th><th>Trạng thái</th><th>Ngày</th></tr></thead>
                    <tbody>
                      {withdrawals.map(w => (
                        <tr key={w.id}>
                          <td><strong>{w.amount_fmt}</strong></td>
                          <td>{w.bank_name} · {w.account_number}</td>
                          <td><span className={`tag ${getStatusTag(w.status)}`}>{w.status_label}</span></td>
                          <td style={{ fontSize: '13px', color: '#888' }}>{formatDate(w.created_at)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
      <Footer />
    </>
  )
}

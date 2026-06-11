'use client'

import { useState, useEffect, useCallback } from 'react'
import { api, extractError } from '@/lib/api'
import { formatVnd, formatDate, formatNumber, getStatusTag } from '@/lib/utils'
import Pagination from '@/components/ui/Pagination'

interface AffiliateRow {
  id: string
  user_email: string
  user_name: string
  ref_code: string
  is_active: boolean
  total_clicks: number
  total_orders: number
  total_earnings: number
  total_earnings_fmt: string
  paid_earnings: number
  paid_earnings_fmt: string
  pending_withdrawal: number
  pending_withdrawal_fmt: string
}

interface WithdrawalRow {
  id: string
  affiliate_email: string
  amount: number
  amount_fmt: string
  bank_name: string
  account_number: string
  account_name: string
  status: string
  status_label: string
  created_at: string
}

export default function AdminAffiliatePage() {
  const [tab, setTab] = useState<'affiliates' | 'withdrawals'>('affiliates')
  const [affiliates, setAffiliates] = useState<AffiliateRow[]>([])
  const [withdrawals, setWithdrawals] = useState<WithdrawalRow[]>([])
  const [wTotal, setWTotal] = useState(0)
  const [wPage, setWPage] = useState(1)
  const [wStatus, setWStatus] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const fetchAffiliates = useCallback(async () => {
    const { data } = await api.get('/admin/affiliate?page_size=50')
    setAffiliates(data.items || [])
  }, [])

  const fetchWithdrawals = useCallback(async (p = 1) => {
    const params: Record<string, string | number> = { page: p, page_size: 20 }
    if (wStatus) params.status = wStatus
    const { data } = await api.get('/admin/affiliate/withdrawals/all', { params })
    setWithdrawals(data.items || [])
    setWTotal(data.total || 0)
    setWPage(p)
  }, [wStatus])

  useEffect(() => {
    setLoading(true)
    Promise.all([fetchAffiliates(), fetchWithdrawals(1)]).finally(() => setLoading(false))
  }, [fetchAffiliates, fetchWithdrawals])

  const toggleAffiliate = async (id: string) => {
    try { await api.patch(`/admin/affiliate/${id}/toggle`); await fetchAffiliates() }
    catch (err) { setError(extractError(err)) }
  }

  const handleWithdrawal = async (id: string, action: string, note?: string) => {
    try {
      await api.patch(`/admin/affiliate/withdrawals/${id}`, { status: action, admin_note: note })
      await fetchWithdrawals(wPage)
    } catch (err) { setError(extractError(err)) }
  }

  return (
    <>
      <div className="admin-header">
        <h1>Affiliate</h1>
      </div>
      <div className="admin-body">
        {error && <div className="alert alert-error">{error}</div>}
        <div className="tabs">
          <button className={`tab${tab === 'affiliates' ? ' active' : ''}`} onClick={() => setTab('affiliates')}>Affiliates ({affiliates.length})</button>
          <button className={`tab${tab === 'withdrawals' ? ' active' : ''}`} onClick={() => setTab('withdrawals')}>Yêu cầu rút tiền ({wTotal})</button>
        </div>

        {loading ? <div className="skeleton" style={{ height: '400px' }} /> : tab === 'affiliates' ? (
          <div className="card" style={{ padding: 0 }}>
            <div className="table-wrap">
              <table>
                <thead><tr><th>Affiliate</th><th>Ref code</th><th>Clicks</th><th>Đơn</th><th>Hoa hồng</th><th>Đã trả</th><th>Chờ rút</th><th>Trạng thái</th><th>Thao tác</th></tr></thead>
                <tbody>
                  {affiliates.map(a => (
                    <tr key={a.id}>
                      <td>
                        <div style={{ fontWeight: 600 }}>{a.user_name}</div>
                        <div style={{ fontSize: '12px', color: '#888' }}>{a.user_email}</div>
                      </td>
                      <td><span style={{ fontFamily: 'monospace', fontWeight: 700 }}>{a.ref_code}</span></td>
                      <td>{formatNumber(a.total_clicks)}</td>
                      <td>{a.total_orders}</td>
                      <td>{a.total_earnings_fmt}</td>
                      <td>{a.paid_earnings_fmt}</td>
                      <td><strong>{a.pending_withdrawal_fmt}</strong></td>
                      <td><span className={`tag ${a.is_active ? 'tag-success' : 'tag-default'}`}>{a.is_active ? 'Hoạt động' : 'Tạm khóa'}</span></td>
                      <td><button className={`btn btn-sm ${a.is_active ? 'btn-danger' : 'btn-ghost'}`} onClick={() => toggleAffiliate(a.id)}>{a.is_active ? 'Khóa' : 'Kích hoạt'}</button></td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {affiliates.length === 0 && <div className="empty-state">Chưa có affiliate nào</div>}
            </div>
          </div>
        ) : (
          <>
            <div className="filter-bar">
              <select className="form-input" value={wStatus} onChange={e => setWStatus(e.target.value)} style={{ maxWidth: '200px' }}>
                <option value="">Tất cả trạng thái</option>
                <option value="pending">Chờ duyệt</option>
                <option value="approved">Đã duyệt</option>
                <option value="rejected">Từ chối</option>
              </select>
            </div>
            <div className="card" style={{ padding: 0 }}>
              <div className="table-wrap">
                <table>
                  <thead><tr><th>Affiliate</th><th>Số tiền</th><th>Ngân hàng</th><th>Tài khoản</th><th>Trạng thái</th><th>Ngày</th><th>Thao tác</th></tr></thead>
                  <tbody>
                    {withdrawals.map(w => (
                      <tr key={w.id}>
                        <td style={{ fontSize: '13px' }}>{w.affiliate_email}</td>
                        <td><strong>{w.amount_fmt}</strong></td>
                        <td style={{ fontSize: '13px' }}>{w.bank_name}</td>
                        <td style={{ fontSize: '13px' }}>{w.account_number}<br /><span style={{ color: '#888', fontSize: '12px' }}>{w.account_name}</span></td>
                        <td><span className={`tag ${getStatusTag(w.status)}`}>{w.status_label}</span></td>
                        <td style={{ fontSize: '12px', color: '#888' }}>{formatDate(w.created_at)}</td>
                        <td>
                          {w.status === 'pending' && (
                            <div style={{ display: 'flex', gap: '4px' }}>
                              <button className="btn btn-sm" style={{ background: '#27ae60', color: '#fff', border: 'none' }} onClick={() => handleWithdrawal(w.id, 'approved')}>Duyệt</button>
                              <button className="btn btn-danger btn-sm" onClick={() => { const note = prompt('Lý do từ chối:'); if (note !== null) handleWithdrawal(w.id, 'rejected', note) }}>Từ chối</button>
                            </div>
                          )}
                          {w.status === 'approved' && (
                            <button className="btn btn-primary btn-sm" onClick={() => handleWithdrawal(w.id, 'paid')}>Đã chuyển</button>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                {withdrawals.length === 0 && <div className="empty-state">Không có yêu cầu rút tiền</div>}
              </div>
            </div>
            <Pagination page={wPage} totalPages={Math.ceil(wTotal / 20)} onPageChange={fetchWithdrawals} />
          </>
        )}
      </div>
    </>
  )
}

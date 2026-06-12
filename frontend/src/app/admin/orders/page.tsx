'use client'

import { useState, useEffect, useCallback } from 'react'
import { api, extractError } from '@/lib/api'
import { formatVnd, formatDateTime, getStatusTag } from '@/lib/utils'
import Pagination from '@/components/ui/Pagination'
import type { Order, PaginatedResponse } from '@/types'

const STATUS_LABELS: Record<string, string> = {
  '': 'Tất cả',
  pending: 'Chờ thanh toán',
  completed: 'Hoàn thành',
  failed: 'Thất bại',
  refunded: 'Hoàn tiền',
  expired: 'Hết hạn',
}

export default function AdminOrdersPage() {
  const [orders, setOrders] = useState<Order[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [status, setStatus] = useState('')
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const [actionLoading, setActionLoading] = useState<string | null>(null)
  const [error, setError] = useState('')

  const fetch = useCallback(async (p = 1) => {
    setLoading(true)
    try {
      const params: Record<string, string | number> = { page: p, page_size: 20 }
      if (status) params.status = status
      if (search) params.q = search
      const { data } = await api.get<PaginatedResponse<Order>>('/admin/orders', { params })
      setOrders(data.items)
      setTotal(data.total)
      setPage(p)
    } catch { setOrders([]) }
    finally { setLoading(false) }
  }, [status, search])

  useEffect(() => { fetch(1) }, [fetch])

  const updateStatus = async (orderId: string, newStatus: string) => {
    setActionLoading(orderId)
    setError('')
    try {
      await api.patch(`/admin/orders/${orderId}/status`, { status: newStatus })
      await fetch(page)
    } catch (err) {
      setError(extractError(err))
    } finally {
      setActionLoading(null)
    }
  }

  return (
    <>
      <div className="admin-header">
        <h1>Đơn hàng</h1>
        <span style={{ fontSize: '14px', color: '#666' }}>{total} đơn</span>
      </div>
      <div className="admin-body">
        {error && <div className="alert alert-error">{error}</div>}

        <div className="filter-bar">
          <input className="form-input" placeholder="Tìm mã đơn, email..." value={search} onChange={e => setSearch(e.target.value)} onKeyDown={e => e.key === 'Enter' && fetch(1)} style={{ maxWidth: '260px' }} />
          <select className="form-input" value={status} onChange={e => setStatus(e.target.value)} style={{ maxWidth: '200px' }}>
            {Object.entries(STATUS_LABELS).map(([v, l]) => <option key={v} value={v}>{l}</option>)}
          </select>
          <button className="btn btn-primary btn-sm" onClick={() => fetch(1)}>Lọc</button>
        </div>

        {loading ? <div className="skeleton" style={{ height: '400px' }} /> : (
          <div className="card" style={{ padding: 0 }}>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Mã đơn</th>
                    <th>Học viên</th>
                    <th>Khóa học</th>
                    <th>Số tiền</th>
                    <th>Trạng thái</th>
                    <th>Ngày tạo</th>
                    <th>Thao tác</th>
                  </tr>
                </thead>
                <tbody>
                  {orders.map(o => (
                    <tr key={o.id}>
                      <td><span style={{ fontFamily: 'monospace', fontSize: '12px' }}>{o.order_code}</span></td>
                      <td style={{ fontSize: '13px' }}>{o.user?.name || o.user_name || '—'}<br /><span style={{ color: '#888', fontSize: '12px' }}>{o.user?.email || o.user_email}</span></td>
                      <td style={{ fontSize: '13px', maxWidth: '200px' }}>{o.course?.title || o.course_title || '—'}</td>
                      <td><strong>{o.amount_fmt || formatVnd(o.amount)}</strong></td>
                      <td><span className={`tag ${getStatusTag(o.status)}`}>{o.status_label || o.status}</span></td>
                      <td style={{ fontSize: '12px', color: '#888' }}>{formatDateTime(o.created_at)}</td>
                      <td>
                        {o.status === 'pending' && (
                          <div style={{ display: 'flex', gap: '4px' }}>
                            <button className="btn btn-sm" style={{ background: '#27ae60', color: '#fff', border: 'none' }} disabled={actionLoading === o.id} onClick={() => updateStatus(o.id, 'completed')}>Duyệt</button>
                            <button className="btn btn-danger btn-sm" disabled={actionLoading === o.id} onClick={() => updateStatus(o.id, 'failed')}>Từ chối</button>
                          </div>
                        )}
                        {o.status === 'completed' && (
                          <button className="btn btn-sm btn-ghost" disabled={actionLoading === o.id} onClick={() => updateStatus(o.id, 'refunded')}>Hoàn tiền</button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {orders.length === 0 && <div className="empty-state">Không có đơn hàng nào</div>}
            </div>
          </div>
        )}
        <Pagination page={page} totalPages={Math.ceil(total / 20)} onPageChange={fetch} />
      </div>
    </>
  )
}

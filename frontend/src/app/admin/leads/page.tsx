'use client'

import { useState, useEffect, useCallback } from 'react'
import { api, extractError } from '@/lib/api'
import { formatDateTime } from '@/lib/utils'
import Pagination from '@/components/ui/Pagination'
import type { Lead, PaginatedResponse } from '@/types'

export default function AdminLeadsPage() {
  const [leads, setLeads] = useState<Lead[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const [syncing, setSyncing] = useState(false)
  const [error, setError] = useState('')

  const fetch = useCallback(async (p = 1) => {
    setLoading(true)
    try {
      const params: Record<string, string | number> = { page: p, page_size: 20 }
      if (search) params.q = search
      const { data } = await api.get('/admin/leads', { params })
      setLeads(data.items)
      setTotal(data.total)
      setPage(p)
    } catch { setLeads([]) }
    finally { setLoading(false) }
  }, [search])

  useEffect(() => { fetch(1) }, [fetch])

  const syncSheets = async () => {
    setSyncing(true)
    try {
      const { data } = await api.post('/admin/leads/sync-sheets')
      alert(data.message || 'Đồng bộ thành công!')
      await fetch(page)
    } catch (err) {
      setError(extractError(err))
    } finally {
      setSyncing(false)
    }
  }

  return (
    <>
      <div className="admin-header">
        <h1>Leads</h1>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button className="btn btn-ghost btn-sm" onClick={syncSheets} disabled={syncing}>
            {syncing ? <span className="spinner" /> : '🔄 Sync Google Sheets'}
          </button>
        </div>
      </div>
      <div className="admin-body">
        {error && <div className="alert alert-error">{error}</div>}
        <div className="filter-bar">
          <input className="form-input" placeholder="Tìm tên, email, phone..." value={search} onChange={e => setSearch(e.target.value)} onKeyDown={e => e.key === 'Enter' && fetch(1)} style={{ maxWidth: '280px' }} />
          <button className="btn btn-primary btn-sm" onClick={() => fetch(1)}>Lọc</button>
          <span style={{ fontSize: '13px', color: '#666', marginLeft: 'auto' }}>Tổng: {total} leads</span>
        </div>

        {loading ? <div className="skeleton" style={{ height: '400px' }} /> : (
          <div className="card" style={{ padding: 0 }}>
            <div className="table-wrap">
              <table>
                <thead><tr><th>Họ tên</th><th>Email</th><th>SĐT</th><th>Nguồn</th><th>Chiến dịch</th><th>Đã mua</th><th>Đồng bộ</th><th>Ngày</th></tr></thead>
                <tbody>
                  {leads.map(l => (
                    <tr key={l.id}>
                      <td style={{ fontWeight: 600 }}>{l.name}</td>
                      <td style={{ fontSize: '13px' }}>{l.email}</td>
                      <td style={{ fontSize: '13px' }}>{l.phone || '—'}</td>
                      <td><span style={{ fontSize: '12px', background: '#f6f6f6', padding: '2px 6px', borderRadius: '4px' }}>{l.utm_source || 'organic'}</span></td>
                      <td style={{ fontSize: '12px', color: '#888' }}>{l.utm_campaign || '—'}</td>
                      <td><span className={`tag ${l.is_converted ? 'tag-success' : 'tag-default'}`}>{l.is_converted ? 'Đã mua' : 'Chưa mua'}</span></td>
                      <td><span className={`tag ${l.is_synced ? 'tag-info' : 'tag-default'}`}>{l.is_synced ? 'Đã sync' : 'Chưa'}</span></td>
                      <td style={{ fontSize: '12px', color: '#888' }}>{formatDateTime(l.created_at)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {leads.length === 0 && <div className="empty-state">Chưa có lead nào</div>}
            </div>
          </div>
        )}
        <Pagination page={page} totalPages={Math.ceil(total / 20)} onPageChange={fetch} />
      </div>
    </>
  )
}

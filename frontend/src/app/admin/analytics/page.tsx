'use client'

import { useState, useEffect } from 'react'
import { api } from '@/lib/api'
import { formatVnd, formatNumber } from '@/lib/utils'

interface RevenueData {
  period: string
  total_revenue: number
  total_revenue_fmt: string
  total_orders: number
  data: Array<{ label: string; revenue: number; revenue_fmt: string; orders_count: number }>
}

interface FunnelStep {
  step: number
  label: string
  count: number
  count_fmt: string
  cvr_from_prev_fmt?: string
}

interface UtmRow {
  utm_source: string
  utm_medium: string
  utm_campaign: string
  orders: number
  revenue: number
  revenue_fmt: string
}

export default function AdminAnalyticsPage() {
  const [period, setPeriod] = useState('30d')
  const [revenue, setRevenue] = useState<RevenueData | null>(null)
  const [funnel, setFunnel] = useState<FunnelStep[]>([])
  const [utmRows, setUtmRows] = useState<UtmRow[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    Promise.all([
      api.get(`/admin/analytics/revenue?period=${period}`),
      api.get('/admin/analytics/funnel'),
      api.get('/admin/analytics/utm-campaigns'),
    ]).then(([r, f, u]) => {
      setRevenue(r.data)
      setFunnel(f.data)
      setUtmRows(u.data)
    }).catch(() => {}).finally(() => setLoading(false))
  }, [period])

  return (
    <>
      <div className="admin-header">
        <h1>Analytics</h1>
        <div style={{ display: 'flex', gap: '6px' }}>
          {['7d', '30d', '90d', '12m'].map(p => (
            <button key={p} className={`btn btn-sm ${period === p ? 'btn-primary' : 'btn-ghost'}`} onClick={() => setPeriod(p)}>
              {p === '12m' ? '12 tháng' : p}
            </button>
          ))}
        </div>
      </div>
      <div className="admin-body">
        {loading ? (
          <div className="grid-2" style={{ gap: '20px' }}>
            {Array.from({ length: 4 }).map((_, i) => <div key={i} className="skeleton" style={{ height: '200px' }} />)}
          </div>
        ) : (
          <>
            {/* Revenue summary */}
            {revenue && (
              <div className="grid-2" style={{ marginBottom: '20px' }}>
                <div className="card">
                  <h3 style={{ fontWeight: 700, marginBottom: '16px' }}>Doanh thu ({period})</h3>
                  <div style={{ display: 'flex', gap: '24px', marginBottom: '16px' }}>
                    <div>
                      <div style={{ fontSize: '13px', color: '#666' }}>Tổng doanh thu</div>
                      <div style={{ fontSize: '24px', fontWeight: 900 }}>{revenue.total_revenue_fmt}</div>
                    </div>
                    <div>
                      <div style={{ fontSize: '13px', color: '#666' }}>Số đơn</div>
                      <div style={{ fontSize: '24px', fontWeight: 900 }}>{formatNumber(revenue.total_orders)}</div>
                    </div>
                  </div>
                  {/* Chart */}
                  <div style={{ display: 'flex', alignItems: 'flex-end', gap: '2px', height: '100px' }}>
                    {(() => {
                      const maxR = Math.max(...revenue.data.map(d => d.revenue), 1)
                      return revenue.data.map((d, i) => (
                        <div key={i} title={`${d.label}: ${d.revenue_fmt}`} style={{ flex: 1, background: d.revenue > 0 ? '#111' : '#e8e8e8', height: `${(d.revenue / maxR) * 100}%`, minHeight: '2px', borderRadius: '2px 2px 0 0' }} />
                      ))
                    })()}
                  </div>
                </div>

                {/* Funnel */}
                <div className="card">
                  <h3 style={{ fontWeight: 700, marginBottom: '16px' }}>Funnel chuyển đổi</h3>
                  {funnel.map((step, i) => (
                    <div key={step.step} style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
                      <div style={{ width: '24px', height: '24px', background: '#111', color: '#fff', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '12px', fontWeight: 700, flexShrink: 0 }}>{step.step}</div>
                      <div style={{ flex: 1 }}>
                        <div style={{ fontSize: '14px', fontWeight: 600 }}>{step.label}</div>
                        {step.cvr_from_prev_fmt && <div style={{ fontSize: '12px', color: '#888' }}>CVR: {step.cvr_from_prev_fmt}</div>}
                      </div>
                      <div style={{ fontWeight: 700 }}>{step.count_fmt}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* UTM */}
            <div className="card" style={{ padding: 0 }}>
              <div style={{ padding: '16px 20px', borderBottom: '1px solid #eee' }}>
                <h3 style={{ fontWeight: 700 }}>Hiệu quả UTM Campaign</h3>
              </div>
              <div className="table-wrap">
                <table>
                  <thead><tr><th>Source</th><th>Medium</th><th>Campaign</th><th>Đơn hàng</th><th>Doanh thu</th></tr></thead>
                  <tbody>
                    {utmRows.map((r, i) => (
                      <tr key={i}>
                        <td><span style={{ fontSize: '12px', background: '#f6f6f6', padding: '2px 6px', borderRadius: '4px' }}>{r.utm_source || '(none)'}</span></td>
                        <td style={{ fontSize: '13px' }}>{r.utm_medium || '—'}</td>
                        <td style={{ fontSize: '13px' }}>{r.utm_campaign}</td>
                        <td>{r.orders}</td>
                        <td><strong>{r.revenue_fmt}</strong></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                {utmRows.length === 0 && <div className="empty-state" style={{ padding: '32px' }}>Chưa có dữ liệu UTM</div>}
              </div>
            </div>
          </>
        )}
      </div>
    </>
  )
}

'use client'

import { useState, useEffect } from 'react'
import { api } from '@/lib/api'
import { formatVnd, formatNumber, formatDate } from '@/lib/utils'

interface Overview {
  revenue_today_fmt: string
  revenue_this_month_fmt: string
  revenue_change_pct_fmt: string
  revenue_change_positive: boolean
  orders_today_fmt: string
  orders_this_month_fmt: string
  new_students_fmt: string
  total_students_fmt: string
  leads_this_month_fmt: string
  revenue_30_days: Array<{ date: string; revenue: number; orders_count: number }>
  top_courses: Array<{ course_id: string; title: string; revenue_fmt: string; orders_count: number }>
}

export default function AdminDashboardPage() {
  const [data, setData] = useState<Overview | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/admin/analytics/overview').then(r => setData(r.data)).catch(() => {}).finally(() => setLoading(false))
  }, [])

  return (
    <>
      <div className="admin-header">
        <h1>Dashboard</h1>
        <span style={{ fontSize: '13px', color: '#888' }}>{new Date().toLocaleDateString('vi-VN', { weekday: 'long', day: '2-digit', month: '2-digit', year: 'numeric', timeZone: 'Asia/Ho_Chi_Minh' })}</span>
      </div>
      <div className="admin-body">
        {loading ? (
          <div className="metric-grid">
            {Array.from({ length: 8 }).map((_, i) => <div key={i} className="skeleton" style={{ height: '90px' }} />)}
          </div>
        ) : data ? (
          <>
            <div className="metric-grid" style={{ gridTemplateColumns: 'repeat(4,1fr)' }}>
              {[
                { label: 'Doanh thu hôm nay', value: data.revenue_today_fmt },
                { label: 'Doanh thu tháng này', value: data.revenue_this_month_fmt, change: data.revenue_change_pct_fmt, positive: data.revenue_change_positive },
                { label: 'Đơn hôm nay', value: data.orders_today_fmt },
                { label: 'Đơn tháng này', value: data.orders_this_month_fmt },
                { label: 'HV mới tháng này', value: data.new_students_fmt },
                { label: 'Tổng học viên', value: data.total_students_fmt },
                { label: 'Leads tháng này', value: data.leads_this_month_fmt },
              ].map(m => (
                <div key={m.label} className="metric-card">
                  <div className="metric-label">{m.label}</div>
                  <div className="metric-value">{m.value}</div>
                  {m.change && <div className={`metric-change ${m.positive ? 'positive' : 'negative'}`}>{m.change}</div>}
                </div>
              ))}
            </div>

            <div className="grid-2" style={{ gap: '20px', marginTop: '20px' }}>
              {/* Revenue chart (simple bar) */}
              <div className="card">
                <h3 style={{ fontWeight: 700, marginBottom: '16px' }}>Doanh thu 30 ngày</h3>
                <div style={{ display: 'flex', alignItems: 'flex-end', gap: '3px', height: '120px' }}>
                  {(() => {
                    const maxRev = Math.max(...data.revenue_30_days.map(d => d.revenue), 1)
                    return data.revenue_30_days.map((d, i) => (
                      <div key={i} title={`${d.date}: ${formatVnd(d.revenue)}`} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '2px' }}>
                        <div style={{ width: '100%', background: d.revenue > 0 ? '#111' : '#e8e8e8', height: `${(d.revenue / maxRev) * 100}%`, minHeight: d.revenue > 0 ? '4px' : '2px', borderRadius: '2px 2px 0 0' }} />
                      </div>
                    ))
                  })()}
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: '#888', marginTop: '8px' }}>
                  <span>{data.revenue_30_days[0]?.date}</span>
                  <span>{data.revenue_30_days[data.revenue_30_days.length - 1]?.date}</span>
                </div>
              </div>

              {/* Top courses */}
              <div className="card">
                <h3 style={{ fontWeight: 700, marginBottom: '16px' }}>Top khóa học</h3>
                {data.top_courses.map((c, i) => (
                  <div key={c.course_id} style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
                    <div style={{ width: '24px', height: '24px', background: '#111', color: '#fff', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '12px', fontWeight: 700, flexShrink: 0 }}>{i + 1}</div>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ fontSize: '13px', fontWeight: 600, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{c.title}</div>
                      <div style={{ fontSize: '12px', color: '#888' }}>{c.orders_count} đơn</div>
                    </div>
                    <div style={{ fontSize: '14px', fontWeight: 700, flexShrink: 0 }}>{c.revenue_fmt}</div>
                  </div>
                ))}
              </div>
            </div>
          </>
        ) : (
          <div className="alert alert-error">Không thể tải dữ liệu dashboard</div>
        )}
      </div>
    </>
  )
}

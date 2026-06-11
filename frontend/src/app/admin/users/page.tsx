'use client'

import { useState, useEffect, useCallback } from 'react'
import { api, extractError } from '@/lib/api'
import { formatDate, getStatusTag } from '@/lib/utils'
import Pagination from '@/components/ui/Pagination'
import type { User, PaginatedResponse } from '@/types'

export default function AdminUsersPage() {
  const [users, setUsers] = useState<(User & { courses_count?: number; total_spent?: number; total_spent_fmt?: string })[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [role, setRole] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const fetch = useCallback(async (p = 1) => {
    setLoading(true)
    try {
      const params: Record<string, string | number> = { page: p, page_size: 20 }
      if (search) params.q = search
      if (role) params.role = role
      const { data } = await api.get('/admin/users', { params })
      setUsers(data.items)
      setTotal(data.total)
      setPage(p)
    } catch { setUsers([]) }
    finally { setLoading(false) }
  }, [search, role])

  useEffect(() => { fetch(1) }, [fetch])

  const toggleActive = async (userId: string, isActive: boolean) => {
    setError('')
    try {
      await api.patch(`/admin/users/${userId}`, { is_active: !isActive })
      await fetch(page)
    } catch (err) { setError(extractError(err)) }
  }

  return (
    <>
      <div className="admin-header">
        <h1>Thành viên</h1>
        <span style={{ fontSize: '14px', color: '#666' }}>{total} người dùng</span>
      </div>
      <div className="admin-body">
        {error && <div className="alert alert-error">{error}</div>}
        <div className="filter-bar">
          <input className="form-input" placeholder="Tìm tên, email..." value={search} onChange={e => setSearch(e.target.value)} onKeyDown={e => e.key === 'Enter' && fetch(1)} style={{ maxWidth: '260px' }} />
          <select className="form-input" value={role} onChange={e => setRole(e.target.value)} style={{ maxWidth: '160px' }}>
            <option value="">Tất cả vai trò</option>
            <option value="student">Học viên</option>
            <option value="admin">Admin</option>
          </select>
          <button className="btn btn-primary btn-sm" onClick={() => fetch(1)}>Lọc</button>
        </div>

        {loading ? <div className="skeleton" style={{ height: '400px' }} /> : (
          <div className="card" style={{ padding: 0 }}>
            <div className="table-wrap">
              <table>
                <thead><tr><th>Người dùng</th><th>Vai trò</th><th>KH đã mua</th><th>Tổng chi tiêu</th><th>Trạng thái</th><th>Ngày đăng ký</th><th>Thao tác</th></tr></thead>
                <tbody>
                  {users.map(u => (
                    <tr key={u.id}>
                      <td>
                        <div style={{ fontWeight: 600 }}>{u.name}</div>
                        <div style={{ fontSize: '12px', color: '#888' }}>{u.email}</div>
                      </td>
                      <td><span className={`tag ${u.role === 'admin' ? 'tag-info' : 'tag-default'}`}>{u.role === 'admin' ? 'Admin' : 'Học viên'}</span></td>
                      <td>{u.courses_count || 0}</td>
                      <td>{u.total_spent_fmt || '0 ₫'}</td>
                      <td><span className={`tag ${u.is_active ? 'tag-success' : 'tag-danger'}`}>{u.is_active ? 'Hoạt động' : 'Bị khóa'}</span></td>
                      <td style={{ fontSize: '12px', color: '#888' }}>{formatDate(u.created_at)}</td>
                      <td>
                        <button className={`btn btn-sm ${u.is_active ? 'btn-danger' : 'btn-ghost'}`} onClick={() => toggleActive(u.id, !!u.is_active)}>
                          {u.is_active ? 'Khóa' : 'Mở khóa'}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {users.length === 0 && <div className="empty-state">Không có người dùng nào</div>}
            </div>
          </div>
        )}
        <Pagination page={page} totalPages={Math.ceil(total / 20)} onPageChange={fetch} />
      </div>
    </>
  )
}

'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useAuth } from '@/lib/auth'

const navGroups = [
  {
    label: 'Tổng quan',
    items: [
      { href: '/admin', label: 'Dashboard', icon: '📊' },
      { href: '/admin/analytics', label: 'Analytics', icon: '📈' },
    ],
  },
  {
    label: 'Nội dung',
    items: [
      { href: '/admin/courses', label: 'Khóa học', icon: '🎓' },
      { href: '/admin/blog', label: 'Blog', icon: '✍️' },
    ],
  },
  {
    label: 'Kinh doanh',
    items: [
      { href: '/admin/orders', label: 'Đơn hàng', icon: '📦' },
      { href: '/admin/coupons', label: 'Mã giảm giá', icon: '🏷️' },
      { href: '/admin/affiliate', label: 'Affiliate', icon: '🤝' },
    ],
  },
  {
    label: 'Người dùng',
    items: [
      { href: '/admin/users', label: 'Thành viên', icon: '👥' },
      { href: '/admin/leads', label: 'Leads', icon: '📋' },
    ],
  },
  {
    label: 'Hệ thống',
    items: [
      { href: '/admin/settings', label: 'Cài đặt', icon: '⚙️' },
    ],
  },
]

export default function AdminSidebar() {
  const pathname = usePathname()
  const { logout, user } = useAuth()

  const isActive = (href: string) => {
    if (href === '/admin') return pathname === '/admin'
    return pathname.startsWith(href)
  }

  return (
    <aside className="admin-sidebar">
      <div className="admin-sidebar-logo">
        <Link href="/" style={{ textDecoration: 'none', color: 'inherit' }}>EduVietPro</Link>
        <div style={{ fontSize: '11px', color: '#999', fontWeight: 400, marginTop: '2px' }}>Admin Panel</div>
      </div>

      {navGroups.map((group) => (
        <div key={group.label} className="admin-sidebar-group">
          <div className="admin-sidebar-group-label">{group.label}</div>
          {group.items.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={`admin-sidebar-item${isActive(item.href) ? ' active' : ''}`}
            >
              <span style={{ width: 18, textAlign: 'center' }}>{item.icon}</span>
              {item.label}
            </Link>
          ))}
        </div>
      ))}

      <div style={{ marginTop: 'auto', padding: '16px 20px', borderTop: '1px solid #eee' }}>
        <div style={{ fontSize: '13px', color: '#666', marginBottom: '8px' }}>
          {user?.name}
        </div>
        <Link href="/" className="admin-sidebar-item" style={{ padding: '6px 0' }}>
          <span>🏠</span> Trang chủ
        </Link>
        <button
          onClick={logout}
          className="admin-sidebar-item"
          style={{ width: '100%', background: 'none', border: 'none', cursor: 'pointer', padding: '6px 0', textAlign: 'left', fontFamily: 'inherit' }}
        >
          <span>🚪</span> Đăng xuất
        </button>
      </div>
    </aside>
  )
}

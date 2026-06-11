'use client'

import { useState, useRef, useEffect } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useAuth } from '@/lib/auth'
import { getInitials } from '@/lib/utils'

export default function Navbar() {
  const { user, logout } = useAuth()
  const pathname = usePathname()
  const [open, setOpen] = useState(false)
  const dropRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (dropRef.current && !dropRef.current.contains(e.target as Node)) {
        setOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClick)
    return () => document.removeEventListener('mousedown', handleClick)
  }, [])

  return (
    <header className="nav">
      <div className="container">
        <nav className="nav-inner">
          <Link href="/" className="nav-logo">Tú Marketing</Link>

          <ul className="nav-links">
            <li><Link href="/courses" className={pathname.startsWith('/courses') ? 'active' : ''}>Khóa học</Link></li>
            <li><Link href="/blog" className={pathname.startsWith('/blog') ? 'active' : ''}>Blog</Link></li>
          </ul>

          <div className="nav-right">
            {user ? (
              <div style={{ position: 'relative' }} ref={dropRef}>
                <div className="nav-avatar" onClick={() => setOpen(!open)} title={user.name}>
                  {user.avatar_url
                    ? <img src={user.avatar_url} alt={user.name} style={{ width: '100%', height: '100%', borderRadius: '50%', objectFit: 'cover' }} />
                    : getInitials(user.name)
                  }
                </div>
                {open && (
                  <div className="nav-dropdown">
                    <div style={{ padding: '8px 16px 4px', fontSize: '13px', color: '#666' }}>
                      <div style={{ fontWeight: 700, color: '#111' }}>{user.name}</div>
                      <div>{user.email}</div>
                    </div>
                    <div className="nav-dropdown-divider" />
                    <Link href="/dashboard" onClick={() => setOpen(false)}>Khóa học của tôi</Link>
                    <Link href="/dashboard/profile" onClick={() => setOpen(false)}>Hồ sơ</Link>
                    <Link href="/dashboard/affiliate" onClick={() => setOpen(false)}>Affiliate</Link>
                    {user.role === 'admin' && (
                      <>
                        <div className="nav-dropdown-divider" />
                        <Link href="/admin" onClick={() => setOpen(false)}>Quản trị</Link>
                      </>
                    )}
                    <div className="nav-dropdown-divider" />
                    <button onClick={() => { setOpen(false); logout() }}>Đăng xuất</button>
                  </div>
                )}
              </div>
            ) : (
              <>
                <Link href="/login" className="btn btn-ghost btn-sm">Đăng nhập</Link>
                <Link href="/register" className="btn btn-primary btn-sm">Đăng ký</Link>
              </>
            )}
          </div>
        </nav>
      </div>
    </header>
  )
}

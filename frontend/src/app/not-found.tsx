import Link from 'next/link'

export default function NotFound() {
  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#f6f6f6', textAlign: 'center', padding: '24px' }}>
      <div>
        <div style={{ fontSize: '80px', fontWeight: 900, color: '#111', lineHeight: 1 }}>404</div>
        <h1 style={{ fontSize: '24px', fontWeight: 800, marginTop: '16px', marginBottom: '8px' }}>Trang không tìm thấy</h1>
        <p style={{ color: '#666', marginBottom: '24px' }}>Trang bạn đang tìm kiếm không tồn tại hoặc đã bị xóa.</p>
        <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
          <Link href="/" className="btn btn-primary">Về trang chủ</Link>
          <Link href="/courses" className="btn btn-ghost">Xem khóa học</Link>
        </div>
      </div>
    </div>
  )
}

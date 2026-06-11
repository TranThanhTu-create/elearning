import Link from 'next/link'

export default function CheckoutExpiredPage() {
  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#f6f6f6', padding: '24px' }}>
      <div style={{ textAlign: 'center', maxWidth: '440px' }}>
        <div style={{ fontSize: '72px', marginBottom: '16px' }}>⏰</div>
        <h1 style={{ fontSize: '26px', fontWeight: 800, marginBottom: '12px' }}>Đơn hàng đã hết hạn</h1>
        <p style={{ color: '#666', lineHeight: 1.6, marginBottom: '24px' }}>
          Phiên thanh toán của bạn đã hết hạn. Vui lòng thực hiện lại quá trình mua khóa học.
        </p>
        <div style={{ display: 'flex', gap: '12px', justifyContent: 'center', flexWrap: 'wrap' }}>
          <Link href="/courses" className="btn btn-primary btn-lg">Mua lại</Link>
          <Link href="/dashboard" className="btn btn-ghost">Trang học</Link>
        </div>
      </div>
    </div>
  )
}

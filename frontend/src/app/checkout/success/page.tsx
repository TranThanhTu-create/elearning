'use client'

import { Suspense } from 'react'
import Link from 'next/link'
import { useSearchParams } from 'next/navigation'

function SuccessContent() {
  const params = useSearchParams()
  const orderCode = params.get('order')

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#f6f6f6', padding: '24px' }}>
      <div style={{ textAlign: 'center', maxWidth: '440px' }}>
        <div style={{ fontSize: '72px', marginBottom: '16px' }}>🎉</div>
        <h1 style={{ fontSize: '26px', fontWeight: 800, marginBottom: '12px' }}>Thanh toán thành công!</h1>
        <p style={{ color: '#666', lineHeight: 1.6, marginBottom: '24px' }}>
          Cảm ơn bạn đã mua khóa học. Đơn hàng {orderCode && <strong>#{orderCode}</strong>} đã được xác nhận.
          Bạn có thể bắt đầu học ngay bây giờ!
        </p>
        <div style={{ display: 'flex', gap: '12px', justifyContent: 'center', flexWrap: 'wrap' }}>
          <Link href="/dashboard" className="btn btn-primary btn-lg">Vào học ngay →</Link>
          <Link href="/courses" className="btn btn-ghost">Xem khóa học khác</Link>
        </div>
      </div>
    </div>
  )
}

export default function CheckoutSuccessPage() {
  return <Suspense><SuccessContent /></Suspense>
}

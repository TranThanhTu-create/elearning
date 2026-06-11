'use client'

import { useState, useEffect, useRef } from 'react'
import { useParams, useRouter } from 'next/navigation'
import Link from 'next/link'
import Navbar from '@/components/layout/Navbar'
import { api, extractError } from '@/lib/api'
import { formatVnd, formatDateTime } from '@/lib/utils'
import type { Order } from '@/types'

export default function CheckoutPage() {
  const { orderCode } = useParams<{ orderCode: string }>()
  const router = useRouter()
  const [order, setOrder] = useState<Order | null>(null)
  const [loading, setLoading] = useState(true)
  const [couponCode, setCouponCode] = useState('')
  const [applyingCoupon, setApplyingCoupon] = useState(false)
  const [couponError, setCouponError] = useState('')
  const [timeLeft, setTimeLeft] = useState(0)
  const pollRef = useRef<NodeJS.Timeout | null>(null)

  const fetchOrder = async () => {
    try {
      const { data } = await api.get<Order>(`/orders/${orderCode}`)
      setOrder(data)
      if (data.status === 'completed') {
        router.push('/checkout/success?order=' + orderCode)
      }
      if (data.status === 'expired') {
        router.push('/checkout/expired')
      }
      if (data.expires_at) {
        setTimeLeft(Math.max(0, Math.floor((new Date(data.expires_at).getTime() - Date.now()) / 1000)))
      }
    } catch {
      router.push('/dashboard')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchOrder()
    pollRef.current = setInterval(fetchOrder, 5000)
    return () => { if (pollRef.current) clearInterval(pollRef.current) }
  }, [orderCode])

  useEffect(() => {
    if (timeLeft <= 0) return
    const t = setInterval(() => setTimeLeft(s => Math.max(0, s - 1)), 1000)
    return () => clearInterval(t)
  }, [timeLeft])

  const applyCoupon = async () => {
    if (!couponCode.trim()) return
    setApplyingCoupon(true)
    setCouponError('')
    try {
      const { data } = await api.post(`/orders/${orderCode}/apply-coupon`, { coupon_code: couponCode.trim() })
      setOrder(data)
    } catch (err) {
      setCouponError(extractError(err))
    } finally {
      setApplyingCoupon(false)
    }
  }

  const formatTime = (s: number) => `${Math.floor(s / 60).toString().padStart(2, '0')}:${(s % 60).toString().padStart(2, '0')}`

  if (loading) return (
    <>
      <Navbar />
      <div className="container section" style={{ textAlign: 'center' }}>
        <span className="spinner" style={{ width: '32px', height: '32px', borderWidth: '3px' }} />
        <p style={{ marginTop: '12px', color: '#666' }}>Đang tải thông tin thanh toán...</p>
      </div>
    </>
  )

  if (!order) return null

  const bi = order.bank_transfer_info

  return (
    <>
      <Navbar />
      <main className="section-sm">
        <div className="container" style={{ maxWidth: '860px', margin: '0 auto' }}>
          <h1 style={{ fontSize: '22px', fontWeight: 800, marginBottom: '4px' }}>Thanh toán</h1>
          <p style={{ color: '#666', marginBottom: '24px' }}>Đơn hàng #{order.order_code}</p>

          <div className="layout-sidebar" style={{ gridTemplateColumns: '1fr 340px' }}>
            {/* Left: QR & instructions */}
            <div>
              {/* Timer */}
              {timeLeft > 0 && (
                <div className="alert alert-warning" style={{ marginBottom: '16px' }}>
                  ⏱️ Đơn hàng sẽ hết hạn sau <strong>{formatTime(timeLeft)}</strong>
                </div>
              )}

              {bi && (
                <div className="card-dark" style={{ marginBottom: '16px' }}>
                  <h3 style={{ fontWeight: 700, marginBottom: '16px' }}>Chuyển khoản ngân hàng</h3>
                  <div style={{ display: 'flex', gap: '24px', flexWrap: 'wrap' }}>
                    {bi.qr_url && (
                      <div style={{ textAlign: 'center' }}>
                        <img src={bi.qr_url} alt="QR Code" style={{ width: '180px', height: '180px', border: '4px solid #111', borderRadius: '8px' }} />
                        <p style={{ fontSize: '13px', color: '#666', marginTop: '8px' }}>Quét QR để thanh toán</p>
                      </div>
                    )}
                    <div style={{ flex: 1, minWidth: '200px' }}>
                      {[
                        ['Ngân hàng', bi.bank_name],
                        ['Số tài khoản', bi.account_number],
                        ['Chủ tài khoản', bi.account_name],
                        ['Số tiền', formatVnd(bi.amount)],
                        ['Nội dung CK', bi.transfer_content],
                      ].map(([label, val]) => (
                        <div key={label} style={{ marginBottom: '10px' }}>
                          <div style={{ fontSize: '12px', color: '#888', marginBottom: '2px' }}>{label}</div>
                          <div
                            style={{ fontWeight: 700, fontSize: '14px', cursor: 'copy' }}
                            onClick={() => navigator.clipboard.writeText(val).catch(() => {})}
                            title="Click để copy"
                          >
                            {val}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                  <div className="alert alert-info" style={{ marginTop: '16px', marginBottom: 0 }}>
                    Sau khi chuyển khoản, hệ thống sẽ tự động xác nhận trong 1-5 phút. Vui lòng <strong>nhập đúng nội dung chuyển khoản</strong>.
                  </div>
                </div>
              )}

              {/* Coupon */}
              <div className="card" style={{ marginBottom: '16px' }}>
                <h3 style={{ fontWeight: 700, marginBottom: '12px' }}>Mã giảm giá</h3>
                {couponError && <div className="alert alert-error">{couponError}</div>}
                {order.coupon_code ? (
                  <div className="alert alert-success">Đã áp dụng mã: <strong>{order.coupon_code}</strong></div>
                ) : (
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <input className="form-input" value={couponCode} onChange={e => setCouponCode(e.target.value.toUpperCase())} placeholder="Nhập mã giảm giá" style={{ flex: 1 }} />
                    <button className="btn btn-ghost" onClick={applyCoupon} disabled={applyingCoupon}>
                      {applyingCoupon ? <span className="spinner" /> : 'Áp dụng'}
                    </button>
                  </div>
                )}
              </div>
            </div>

            {/* Right: order summary */}
            <div>
              <div className="card-dark">
                <h3 style={{ fontWeight: 700, marginBottom: '16px' }}>Tóm tắt đơn hàng</h3>
                {order.course && (
                  <div style={{ display: 'flex', gap: '12px', marginBottom: '16px', paddingBottom: '16px', borderBottom: '1px solid #eee' }}>
                    {order.course.thumbnail_url && <img src={order.course.thumbnail_url} alt={order.course.title} style={{ width: '60px', height: '45px', objectFit: 'cover', borderRadius: '4px' }} />}
                    <div>
                      <div style={{ fontSize: '14px', fontWeight: 600 }}>{order.course.title}</div>
                      <div style={{ fontSize: '13px', color: '#666' }}>{formatVnd(order.course.price)}</div>
                    </div>
                  </div>
                )}
                <div style={{ fontSize: '14px' }}>
                  {([
                    ['Giá gốc', formatVnd(order.course?.original_price || order.amount)],
                    ...(order.discount_amount ? [['Giảm giá', `- ${formatVnd(order.discount_amount)}`]] : []),
                  ] as [string, string][]).map(([l, v]) => (
                    <div key={l} style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', color: '#666' }}>
                      <span>{l}</span><span>{v}</span>
                    </div>
                  ))}
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: 800, fontSize: '18px', paddingTop: '8px', borderTop: '2px solid #111' }}>
                    <span>Tổng cộng</span>
                    <span>{formatVnd(order.amount)}</span>
                  </div>
                </div>
              </div>
              <div style={{ textAlign: 'center', marginTop: '12px' }}>
                <div style={{ fontSize: '12px', color: '#888' }}>Hết hạn: {formatDateTime(order.expires_at)}</div>
                <Link href="/dashboard" style={{ fontSize: '13px', color: '#666', textDecoration: 'none', display: 'block', marginTop: '8px' }}>← Về trang học</Link>
              </div>
            </div>
          </div>
        </div>
      </main>
    </>
  )
}

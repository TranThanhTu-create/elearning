import Link from 'next/link'

export default function Footer() {
  return (
    <footer className="footer">
      <div className="container">
        <div className="footer-grid">
          <div className="footer-brand">
            <div style={{ fontSize: '22px', fontWeight: 900, background: 'linear-gradient(135deg, #00d4ff 0%, #7b2fff 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text', letterSpacing: '-0.5px' }}>Tú Marketing</div>
            <p>Đào tạo AI Agent & Marketing Automation thực chiến hàng đầu Việt Nam.</p>
          </div>
          <div className="footer-col">
            <h4>Khóa học</h4>
            <ul>
              <li><Link href="/courses">Tất cả khóa học</Link></li>
              <li><Link href="/courses?level=beginner">Dành cho người mới</Link></li>
              <li><Link href="/courses?level=advanced">Nâng cao</Link></li>
            </ul>
          </div>
          <div className="footer-col">
            <h4>Hỗ trợ</h4>
            <ul>
              <li><Link href="/blog">Blog</Link></li>
              <li><Link href="/lien-he">Liên hệ</Link></li>
              <li><Link href="/chinh-sach-bao-mat">Chính sách bảo mật</Link></li>
              <li><Link href="/dieu-khoan">Điều khoản</Link></li>
            </ul>
          </div>
          <div className="footer-col">
            <h4>Tài khoản</h4>
            <ul>
              <li><Link href="/login">Đăng nhập</Link></li>
              <li><Link href="/register">Đăng ký</Link></li>
              <li><Link href="/dashboard/affiliate">Kiếm tiền cùng chúng tôi</Link></li>
            </ul>
          </div>
        </div>
        <div className="footer-bottom">
          <span>© {new Date().getFullYear()} Tú Marketing. Bảo lưu mọi quyền.</span>
          <span>Thanh toán an toàn qua SePay</span>
        </div>
      </div>
    </footer>
  )
}

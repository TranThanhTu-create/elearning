import Link from 'next/link'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Chính sách bảo mật',
}

export default function PrivacyPage() {
  return (
    <div style={{ background: 'var(--bg)', minHeight: '100vh' }}>
      {/* Header */}
      <header style={{ borderBottom: '1px solid var(--border)', padding: '0 24px', height: '60px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', background: 'rgba(7,11,20,0.92)', backdropFilter: 'blur(20px)', position: 'sticky', top: 0, zIndex: 100 }}>
        <Link href="/" style={{ fontSize: '20px', fontWeight: 900, background: 'linear-gradient(135deg, #00d4ff, #7b2fff)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text', textDecoration: 'none' }}>
          Tú Marketing
        </Link>
        <Link href="/" style={{ fontSize: '13px', color: 'var(--text-muted)', textDecoration: 'none' }}>← Về trang chủ</Link>
      </header>

      <div style={{ maxWidth: '760px', margin: '0 auto', padding: '48px 24px' }}>
        <h1 style={{ fontSize: 'clamp(26px, 4vw, 38px)', fontWeight: 900, color: 'var(--text)', marginBottom: '8px', letterSpacing: '-0.5px' }}>
          Chính sách bảo mật
        </h1>
        <p style={{ color: 'var(--text-muted)', marginBottom: '40px', fontSize: '14px' }}>
          Cập nhật lần cuối: 01/06/2026
        </p>

        {[
          {
            title: '1. Thông tin chúng tôi thu thập',
            content: `Khi bạn sử dụng dịch vụ của Tú Marketing, chúng tôi có thể thu thập các loại thông tin sau:

• **Thông tin cá nhân:** Họ tên, địa chỉ email, số điện thoại khi bạn đăng ký tài khoản hoặc điền form.
• **Thông tin thanh toán:** Lịch sử giao dịch, mã đơn hàng (chúng tôi KHÔNG lưu trữ thông tin thẻ ngân hàng).
• **Thông tin sử dụng:** Tiến độ học tập, thời gian truy cập, trang đã xem.
• **Thông tin kỹ thuật:** Địa chỉ IP, loại trình duyệt, hệ điều hành.`,
          },
          {
            title: '2. Mục đích sử dụng thông tin',
            content: `Chúng tôi sử dụng thông tin thu thập để:

• Cung cấp và cải thiện dịch vụ đào tạo của chúng tôi.
• Xử lý thanh toán và gửi xác nhận đơn hàng.
• Gửi thông báo về khóa học, cập nhật nội dung và ưu đãi đặc biệt (có thể hủy đăng ký bất kỳ lúc nào).
• Hỗ trợ kỹ thuật và giải quyết vấn đề.
• Phân tích và cải thiện trải nghiệm người dùng.`,
          },
          {
            title: '3. Bảo mật thông tin',
            content: `Tú Marketing cam kết bảo vệ thông tin cá nhân của bạn:

• Tất cả dữ liệu được truyền qua kết nối HTTPS được mã hóa SSL/TLS.
• Mật khẩu được mã hóa bằng thuật toán bcrypt — chúng tôi không bao giờ lưu mật khẩu dạng văn bản thuần.
• Quyền truy cập vào dữ liệu người dùng được giới hạn chỉ cho nhân viên có thẩm quyền.
• Chúng tôi không bán, cho thuê hoặc chia sẻ thông tin cá nhân của bạn với bên thứ ba vì mục đích thương mại.`,
          },
          {
            title: '4. Chia sẻ thông tin với bên thứ ba',
            content: `Chúng tôi chỉ chia sẻ thông tin trong các trường hợp sau:

• **Đối tác thanh toán:** SePay và ngân hàng để xử lý giao dịch.
• **Dịch vụ email:** Resend.com để gửi email giao dịch và thông báo.
• **Yêu cầu pháp lý:** Khi có yêu cầu hợp pháp từ cơ quan nhà nước có thẩm quyền.

Chúng tôi yêu cầu tất cả đối tác tuân thủ các tiêu chuẩn bảo mật nghiêm ngặt.`,
          },
          {
            title: '5. Cookie và công nghệ theo dõi',
            content: `Chúng tôi sử dụng cookie và công nghệ tương tự để:

• Duy trì phiên đăng nhập của bạn.
• Ghi nhớ tùy chọn và cài đặt của bạn.
• Phân tích lưu lượng truy cập và cải thiện trải nghiệm.

Bạn có thể vô hiệu hóa cookie trong cài đặt trình duyệt, tuy nhiên điều này có thể ảnh hưởng đến một số chức năng của website.`,
          },
          {
            title: '6. Quyền của người dùng',
            content: `Bạn có các quyền sau đối với dữ liệu cá nhân của mình:

• **Quyền truy cập:** Yêu cầu xem thông tin chúng tôi đang lưu trữ về bạn.
• **Quyền chỉnh sửa:** Cập nhật thông tin không chính xác hoặc không đầy đủ.
• **Quyền xóa:** Yêu cầu xóa tài khoản và dữ liệu cá nhân (trừ dữ liệu cần thiết cho nghĩa vụ pháp lý).
• **Quyền phản đối:** Từ chối nhận email marketing bất kỳ lúc nào.

Để thực hiện các quyền này, liên hệ: hello@tumarketing.vn`,
          },
          {
            title: '7. Liên hệ',
            content: `Nếu bạn có bất kỳ câu hỏi nào về chính sách bảo mật này, vui lòng liên hệ:

• **Email:** hello@tumarketing.vn
• **Hotline:** 0909 123 456
• **Địa chỉ:** Việt Nam

Chúng tôi sẽ phản hồi trong vòng 3 ngày làm việc.`,
          },
        ].map(({ title, content }) => (
          <div key={title} style={{ marginBottom: '36px' }}>
            <h2 style={{ fontSize: '18px', fontWeight: 700, color: 'var(--neon)', marginBottom: '12px' }}>{title}</h2>
            <div style={{ fontSize: '15px', color: 'var(--text-muted)', lineHeight: 1.85, whiteSpace: 'pre-line' }}>
              {content.split('**').map((part, i) => i % 2 === 1
                ? <strong key={i} style={{ color: 'var(--text)', fontWeight: 600 }}>{part}</strong>
                : <span key={i}>{part}</span>
              )}
            </div>
          </div>
        ))}

        <div style={{ borderTop: '1px solid var(--border)', paddingTop: '24px', marginTop: '24px' }}>
          <Link href="/dieu-khoan" style={{ color: 'var(--neon)', textDecoration: 'none', fontSize: '14px' }}>
            Xem thêm: Điều khoản sử dụng →
          </Link>
        </div>
      </div>
    </div>
  )
}

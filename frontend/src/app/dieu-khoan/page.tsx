import Link from 'next/link'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Điều khoản sử dụng',
}

export default function TermsPage() {
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
          Điều khoản sử dụng
        </h1>
        <p style={{ color: 'var(--text-muted)', marginBottom: '40px', fontSize: '14px' }}>
          Cập nhật lần cuối: 01/06/2026
        </p>

        {[
          {
            title: '1. Chấp nhận điều khoản',
            content: `Bằng việc truy cập và sử dụng nền tảng Tú Marketing ("Dịch vụ"), bạn đồng ý tuân thủ và bị ràng buộc bởi các điều khoản và điều kiện sau đây. Nếu bạn không đồng ý với bất kỳ phần nào, vui lòng không sử dụng Dịch vụ của chúng tôi.`,
          },
          {
            title: '2. Tài khoản người dùng',
            content: `• Bạn phải cung cấp thông tin chính xác và đầy đủ khi đăng ký.
• Bạn chịu trách nhiệm bảo mật tài khoản và mật khẩu của mình.
• Mỗi tài khoản chỉ được sử dụng bởi một người. Chia sẻ tài khoản là vi phạm điều khoản.
• Tú Marketing có quyền đình chỉ hoặc chấm dứt tài khoản vi phạm điều khoản.
• Bạn phải đủ 18 tuổi hoặc có sự đồng ý của phụ huynh để đăng ký.`,
          },
          {
            title: '3. Quyền sở hữu trí tuệ',
            content: `• Tất cả nội dung trên nền tảng (video, tài liệu, bài viết, hình ảnh) là tài sản của Tú Marketing và được bảo vệ bởi luật sở hữu trí tuệ Việt Nam.
• Khi mua khóa học, bạn nhận được **quyền sử dụng cá nhân** — không được sao chép, chia sẻ, bán lại hoặc phân phối nội dung dưới bất kỳ hình thức nào.
• Vi phạm sở hữu trí tuệ có thể dẫn đến chấm dứt tài khoản và truy cứu pháp lý.`,
          },
          {
            title: '4. Thanh toán và hoàn tiền',
            content: `• Giá khóa học được hiển thị bằng VNĐ và đã bao gồm tất cả các khoản phí.
• Thanh toán được xử lý qua hệ thống ngân hàng an toàn (SePay).
• **Chính sách hoàn tiền:** Trong vòng 7 ngày kể từ khi mua, nếu bạn chưa xem quá 20% nội dung khóa học, bạn có thể yêu cầu hoàn tiền 100%.
• Sau 7 ngày hoặc đã xem quá 20% nội dung, chúng tôi sẽ xem xét từng trường hợp cụ thể.
• Để yêu cầu hoàn tiền, liên hệ: hello@tumarketing.vn`,
          },
          {
            title: '5. Quy tắc sử dụng',
            content: `Khi sử dụng Dịch vụ, bạn cam kết không:

• Chia sẻ tài khoản, mật khẩu hoặc nội dung khóa học với người khác.
• Sử dụng Dịch vụ cho mục đích bất hợp pháp hoặc gây hại.
• Cố gắng hack, phá vỡ hoặc làm gián đoạn hệ thống.
• Đăng tải nội dung vi phạm pháp luật, xúc phạm hoặc spam.
• Sao chép, tái phân phối hoặc kinh doanh lại nội dung của chúng tôi.`,
          },
          {
            title: '6. Giới hạn trách nhiệm',
            content: `• Tú Marketing không đảm bảo kết quả cụ thể từ việc học các khóa học. Thành công phụ thuộc vào nỗ lực và ứng dụng của từng học viên.
• Chúng tôi không chịu trách nhiệm về thiệt hại gián tiếp, đặc biệt hoặc do hệ quả phát sinh từ việc sử dụng hoặc không thể sử dụng Dịch vụ.
• Trách nhiệm tối đa của chúng tôi không vượt quá số tiền bạn đã thanh toán cho Dịch vụ.`,
          },
          {
            title: '7. Thay đổi điều khoản',
            content: `Chúng tôi có thể cập nhật Điều khoản này theo thời gian. Mọi thay đổi sẽ được thông báo qua email đăng ký và cập nhật trên trang này. Việc tiếp tục sử dụng Dịch vụ sau khi thay đổi có hiệu lực đồng nghĩa với việc bạn chấp nhận các điều khoản mới.`,
          },
          {
            title: '8. Liên hệ',
            content: `Nếu bạn có câu hỏi về Điều khoản sử dụng, vui lòng liên hệ:

• **Email:** hello@tumarketing.vn
• **Hotline:** 0909 123 456

Điều khoản này được điều chỉnh bởi pháp luật nước Cộng hòa Xã hội Chủ nghĩa Việt Nam.`,
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
          <Link href="/chinh-sach-bao-mat" style={{ color: 'var(--neon)', textDecoration: 'none', fontSize: '14px' }}>
            Xem thêm: Chính sách bảo mật →
          </Link>
        </div>
      </div>
    </div>
  )
}

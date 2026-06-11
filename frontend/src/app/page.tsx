import Link from 'next/link'
import LandingForm from '@/components/features/LandingForm'

/* ─── Ladipage — Tú Marketing AI Agent Training ─────────── */

export default function HomePage() {
  return (
    <div style={{ background: 'var(--bg)', minHeight: '100vh', fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Inter, sans-serif' }}>

      {/* ── HEADER ──────────────────────────────────────────── */}
      <header style={{
        position: 'sticky', top: 0, zIndex: 100,
        background: 'rgba(7,11,20,0.92)', backdropFilter: 'blur(20px)',
        borderBottom: '1px solid var(--border)', padding: '0 24px',
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        height: '60px',
      }}>
        <div style={{ fontSize: '20px', fontWeight: 900, background: 'linear-gradient(135deg, #00d4ff, #7b2fff)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text', letterSpacing: '-0.5px' }}>
          Tú Marketing
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
          <a href="tel:0909123456" style={{ fontSize: '14px', color: 'var(--text-muted)', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '6px' }}>
            📞 Hotline: <strong style={{ color: 'var(--neon)' }}>0909 123 456</strong>
          </a>
          <a href="#dang-ky" className="btn btn-primary btn-sm">Đăng ký ngay</a>
        </div>
      </header>

      {/* ── HERO ────────────────────────────────────────────── */}
      <section style={{
        position: 'relative', overflow: 'hidden',
        padding: '80px 24px 60px', textAlign: 'center',
        background: 'radial-gradient(ellipse 90% 60% at 50% 0%, rgba(0,212,255,0.14) 0%, transparent 65%), radial-gradient(ellipse 60% 50% at 85% 70%, rgba(123,47,255,0.10) 0%, transparent 60%), #070b14',
      }}>
        {/* grid */}
        <div style={{ position: 'absolute', inset: 0, backgroundImage: 'linear-gradient(rgba(0,212,255,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(0,212,255,0.03) 1px, transparent 1px)', backgroundSize: '60px 60px', pointerEvents: 'none' }} />
        {/* glow orb */}
        <div style={{ position: 'absolute', top: '-80px', left: '50%', transform: 'translateX(-50%)', width: '600px', height: '400px', borderRadius: '50%', background: 'rgba(0,212,255,0.05)', filter: 'blur(100px)', pointerEvents: 'none' }} />

        <div style={{ position: 'relative', maxWidth: '860px', margin: '0 auto' }}>
          {/* urgency badge */}
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: '10px', background: 'rgba(255,107,53,0.12)', border: '1px solid rgba(255,107,53,0.35)', borderRadius: '100px', padding: '7px 18px', fontSize: '13px', color: '#ff6b35', marginBottom: '28px', fontWeight: 700 }}>
            🔥 TRAINING TRỰC TIẾP — MIỄN PHÍ 100% — Chỉ còn <strong style={{ color: '#ffd32a' }}>47 suất</strong> cuối cùng!
          </div>

          <h1 style={{ fontSize: 'clamp(30px, 5.5vw, 62px)', fontWeight: 900, lineHeight: 1.1, letterSpacing: '-1.5px', marginBottom: '20px' }}>
            <span style={{ display: 'block', color: 'var(--text)', marginBottom: '6px' }}>Khám Phá Bí Mật Xây Dựng</span>
            <span style={{ display: 'block', background: 'linear-gradient(135deg, #00d4ff 0%, #7b2fff 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>AI AGENT TỰ ĐỘNG HÓA MARKETING</span>
            <span style={{ display: 'block', color: 'var(--text)', fontSize: '0.75em', marginTop: '8px' }}>& Tạo Ra Dòng Thu Nhập Thụ Động 24/7</span>
          </h1>

          <p style={{ fontSize: '18px', color: 'var(--text-muted)', maxWidth: '640px', margin: '0 auto 16px', lineHeight: 1.75 }}>
            Buổi training trực tiếp <strong style={{ color: 'var(--neon)' }}>HOÀN TOÀN MIỄN PHÍ</strong> cùng <strong style={{ color: 'var(--text)' }}>Tú Marketing</strong> — Chuyên gia 14+ năm kinh nghiệm.
            Học cách build AI Agent không cần code, tự động hóa Marketing & tăng doanh thu gấp 3 lần.
          </p>

          {/* datetime badge */}
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: '16px', background: 'rgba(0,212,255,0.06)', border: '1px solid rgba(0,212,255,0.2)', borderRadius: '12px', padding: '12px 24px', fontSize: '14px', color: 'var(--text-muted)', marginBottom: '36px', flexWrap: 'wrap', justifyContent: 'center' }}>
            <span>📅 <strong style={{ color: 'var(--text)' }}>Thứ 7, 21/06/2026</strong></span>
            <span style={{ color: 'var(--border-bright)' }}>|</span>
            <span>⏰ <strong style={{ color: 'var(--text)' }}>20:00 — 22:30</strong></span>
            <span style={{ color: 'var(--border-bright)' }}>|</span>
            <span>💻 <strong style={{ color: 'var(--neon)' }}>Online qua Zoom</strong></span>
          </div>

          <div style={{ display: 'flex', gap: '16px', justifyContent: 'center', flexWrap: 'wrap' }}>
            <a href="#dang-ky" className="btn btn-primary btn-xl" style={{ fontSize: '17px', fontWeight: 800 }}>
              🔥 ĐĂNG KÝ THAM GIA MIỄN PHÍ →
            </a>
          </div>
          <p style={{ fontSize: '13px', color: 'var(--text-dim)', marginTop: '12px' }}>
            ✅ Hoàn toàn miễn phí &nbsp;·&nbsp; ✅ Nhận ngay tài liệu độc quyền &nbsp;·&nbsp; ✅ Được vào nhóm Zalo VIP
          </p>
        </div>
      </section>

      {/* ── STATS ───────────────────────────────────────────── */}
      <div style={{ background: 'var(--bg-card)', borderTop: '1px solid var(--border)', borderBottom: '1px solid var(--border)', padding: '32px 24px' }}>
        <div style={{ maxWidth: '900px', margin: '0 auto', display: 'flex', justifyContent: 'center', flexWrap: 'wrap', gap: '0' }}>
          {[
            { value: '5.000+', label: 'Học viên đã training', color: '#00d4ff' },
            { value: '14+',    label: 'Năm kinh nghiệm',       color: '#7b2fff' },
            { value: '300+',   label: 'Doanh nghiệp đồng hành', color: '#ffd32a' },
            { value: '97%',    label: 'Học viên hài lòng',     color: '#00ff88' },
          ].map(({ value, label, color }, i) => (
            <div key={label} style={{ textAlign: 'center', padding: '0 36px', borderRight: i < 3 ? '1px solid var(--border)' : 'none', flex: '1 1 180px' }}>
              <div style={{ fontSize: '36px', fontWeight: 900, color, letterSpacing: '-1px', textShadow: `0 0 20px ${color}50` }}>{value}</div>
              <div style={{ fontSize: '13px', color: 'var(--text-muted)', marginTop: '6px', fontWeight: 500 }}>{label}</div>
            </div>
          ))}
        </div>
      </div>

      {/* ── FOR WHO ─────────────────────────────────────────── */}
      <section style={{ padding: '72px 24px', maxWidth: '1100px', margin: '0 auto' }}>
        <div style={{ textAlign: 'center', marginBottom: '48px' }}>
          <div style={{ fontSize: '12px', fontWeight: 700, color: 'var(--neon)', textTransform: 'uppercase', letterSpacing: '1.5px', marginBottom: '10px' }}>Đối tượng tham gia</div>
          <h2 style={{ fontSize: 'clamp(26px, 3.5vw, 42px)', fontWeight: 800, color: 'var(--text)', letterSpacing: '-0.5px' }}>
            Workshop Dành Cho <span style={{ background: 'linear-gradient(135deg, #00d4ff, #7b2fff)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>Ai?</span>
          </h2>
        </div>
        <div className="grid-4" style={{ gap: '20px' }}>
          {[
            { icon: '🏪', title: 'Chủ doanh nghiệp', desc: 'Muốn tự động hóa vận hành, giảm chi phí nhân sự và scale nhanh hơn', color: '#00d4ff' },
            { icon: '📱', title: 'Marketer & Salesperson', desc: 'Muốn dùng AI để tạo content, chạy ads và chốt đơn tự động 24/7', color: '#7b2fff' },
            { icon: '💼', title: 'Freelancer', desc: 'Muốn tăng thu nhập bằng cách cung cấp dịch vụ AI Agent cho khách hàng', color: '#ffd32a' },
            { icon: '🚀', title: 'Người mới bắt đầu', desc: 'Muốn học AI Agent từ zero — không cần biết code, không cần kỹ thuật', color: '#00ff88' },
          ].map(({ icon, title, desc, color }) => (
            <div key={title} style={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: '14px', padding: '24px', textAlign: 'center', transition: 'border-color 0.2s' }}>
              <div style={{ width: '60px', height: '60px', borderRadius: '50%', background: `${color}15`, border: `2px solid ${color}30`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '28px', margin: '0 auto 16px', boxShadow: `0 0 20px ${color}20` }}>{icon}</div>
              <div style={{ fontSize: '16px', fontWeight: 700, color: 'var(--text)', marginBottom: '8px' }}>{title}</div>
              <p style={{ fontSize: '14px', color: 'var(--text-muted)', lineHeight: 1.7 }}>{desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── PAIN POINTS ─────────────────────────────────────── */}
      <section style={{ padding: '72px 24px', background: 'linear-gradient(180deg, #0a0f1e, var(--bg))' }}>
        <div style={{ maxWidth: '900px', margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: '48px' }}>
            <h2 style={{ fontSize: 'clamp(24px, 3.5vw, 40px)', fontWeight: 800, color: 'var(--text)', letterSpacing: '-0.5px', marginBottom: '12px' }}>
              Bạn Có Đang Gặp Phải <span style={{ color: '#ff4757' }}>Những Vấn Đề Này?</span>
            </h2>
            <p style={{ color: 'var(--text-muted)', fontSize: '16px' }}>Nếu có bất kỳ điều nào dưới đây — buổi training này chính xác là thứ bạn cần</p>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: '16px' }}>
            {[
              'Tốn hàng giờ mỗi ngày làm content, reply tin nhắn, chăm sóc khách hàng thủ công',
              'Chi phí quảng cáo ngày càng tăng nhưng tỷ lệ chuyển đổi không cải thiện',
              'Không có hệ thống — mọi thứ phụ thuộc vào bản thân, đi vắng là kinh doanh đứng lại',
              'Đã nghe nhiều về AI nhưng không biết ứng dụng thực tế vào kinh doanh như thế nào',
              'Sợ tụt hậu khi đối thủ đang dùng AI còn bạn vẫn làm tay',
              'Muốn scale up nhưng không có đủ tiền thuê thêm nhân sự',
            ].map((pain) => (
              <div key={pain} style={{ display: 'flex', gap: '12px', alignItems: 'flex-start', background: 'rgba(255,71,87,0.05)', border: '1px solid rgba(255,71,87,0.15)', borderRadius: '10px', padding: '16px 18px' }}>
                <span style={{ fontSize: '18px', flexShrink: 0, marginTop: '2px' }}>😓</span>
                <span style={{ fontSize: '14px', color: 'var(--text-muted)', lineHeight: 1.7 }}>{pain}</span>
              </div>
            ))}
          </div>
          <div style={{ textAlign: 'center', marginTop: '36px' }}>
            <p style={{ fontSize: '20px', fontWeight: 700, color: 'var(--text)', marginBottom: '8px' }}>
              Đừng lo — <span style={{ color: 'var(--neon)' }}>AI Agent chính là giải pháp</span> cho tất cả những điều trên!
            </p>
            <a href="#dang-ky" className="btn btn-primary btn-lg" style={{ marginTop: '16px' }}>Tôi muốn tìm hiểu ngay →</a>
          </div>
        </div>
      </section>

      {/* ── CURRICULUM ──────────────────────────────────────── */}
      <section style={{ padding: '72px 24px', maxWidth: '1000px', margin: '0 auto' }}>
        <div style={{ textAlign: 'center', marginBottom: '52px' }}>
          <div style={{ fontSize: '12px', fontWeight: 700, color: 'var(--neon)', textTransform: 'uppercase', letterSpacing: '1.5px', marginBottom: '10px' }}>Nội dung training</div>
          <h2 style={{ fontSize: 'clamp(24px, 3.5vw, 42px)', fontWeight: 800, color: 'var(--text)', letterSpacing: '-0.5px', marginBottom: '12px' }}>
            Bạn Sẽ Học Được Gì Trong <br />
            <span style={{ background: 'linear-gradient(135deg, #00d4ff, #7b2fff)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>2.5 Giờ Training Thực Chiến?</span>
          </h2>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {[
            { num: '01', title: 'AI Agent Là Gì & Tại Sao Đây Là Cuộc Cách Mạng', desc: 'Hiểu đúng AI Agent, phân biệt với ChatGPT thông thường, và lý do tại sao 80% công việc marketing có thể tự động hóa ngay hôm nay.', tag: '⚡ Nền tảng', color: '#00d4ff' },
            { num: '02', title: 'Build AI Agent Đầu Tiên — Không Cần 1 Dòng Code', desc: 'Demo live: xây AI Agent tự động trả lời tin nhắn Zalo/Facebook, qualify lead và đẩy vào CRM — hoàn tất trong 45 phút.', tag: '🛠 Thực hành', color: '#7b2fff' },
            { num: '03', title: 'Hệ Thống Marketing Tự Động 24/7', desc: 'Setup chuỗi automation: thu lead → nurture → chốt đơn hoàn toàn tự động. Xem case study doanh nghiệp tăng 300% lead chỉ sau 2 tuần.', tag: '🚀 Case Study', color: '#ffd32a' },
            { num: '04', title: 'Kiếm Tiền Từ AI Agent — 3 Mô Hình Thực Tế', desc: 'Bán dịch vụ AI Agent cho doanh nghiệp, tạo SaaS với AI, hoặc dùng AI để scale business hiện tại. ROI thực tế và lộ trình triển khai.', tag: '💰 Thu nhập', color: '#00ff88' },
          ].map(({ num, title, desc, tag, color }) => (
            <div key={num} style={{ display: 'flex', gap: '20px', background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: '14px', padding: '24px', alignItems: 'flex-start', transition: 'border-color 0.2s' }}>
              <div style={{ width: '52px', height: '52px', borderRadius: '12px', background: `${color}15`, border: `1px solid ${color}30`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '20px', fontWeight: 900, color, flexShrink: 0, boxShadow: `0 0 16px ${color}20` }}>{num}</div>
              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px', flexWrap: 'wrap' }}>
                  <h3 style={{ fontSize: '17px', fontWeight: 700, color: 'var(--text)' }}>{title}</h3>
                  <span style={{ fontSize: '11px', fontWeight: 700, background: `${color}15`, color, border: `1px solid ${color}30`, borderRadius: '6px', padding: '2px 8px', whiteSpace: 'nowrap' }}>{tag}</span>
                </div>
                <p style={{ fontSize: '14px', color: 'var(--text-muted)', lineHeight: 1.75 }}>{desc}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ── BONUSES ─────────────────────────────────────────── */}
      <section style={{ padding: '72px 24px', background: 'linear-gradient(180deg, var(--bg), #0a0f1e)' }}>
        <div style={{ maxWidth: '1000px', margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: '48px' }}>
            <div style={{ fontSize: '12px', fontWeight: 700, color: 'var(--neon-green)', textTransform: 'uppercase', letterSpacing: '1.5px', marginBottom: '10px' }}>Quà tặng đặc biệt</div>
            <h2 style={{ fontSize: 'clamp(24px, 3.5vw, 42px)', fontWeight: 800, color: 'var(--text)', letterSpacing: '-0.5px', marginBottom: '12px' }}>
              Đăng Ký Ngay Hôm Nay — Nhận <span style={{ color: 'var(--neon-green)' }}>MIỄN PHÍ</span> Trọn Bộ
            </h2>
            <p style={{ color: 'var(--text-muted)', fontSize: '16px' }}>Tổng giá trị: <span style={{ textDecoration: 'line-through', color: 'var(--text-dim)' }}>3.000.000đ</span> <strong style={{ color: 'var(--neon-green)', fontSize: '20px' }}>→ MIỄN PHÍ 100%</strong></p>
          </div>
          <div className="grid-3" style={{ gap: '20px' }}>
            {[
              { icon: '🤖', title: 'Bộ 50+ AI Agent Templates', desc: 'Templates sẵn dùng cho Marketing, Sales, CSKH — cài vào dùng ngay, không cần tùy chỉnh', value: '500.000đ', color: '#00d4ff' },
              { icon: '📚', title: 'Ebook: AI Agent A-Z', desc: '120 trang hướng dẫn chi tiết từ cơ bản đến nâng cao, có hình ảnh và video demo', value: '299.000đ', color: '#7b2fff' },
              { icon: '💬', title: 'Nhóm Zalo VIP Trọn Đời', desc: 'Hỗ trợ 1-1 từ Tú và cộng đồng 5.000+ người, cập nhật tools mới mỗi tuần', value: '1.200.000đ', color: '#ffd32a' },
              { icon: '🎥', title: 'Bản Ghi Video Training', desc: 'Xem lại không giới hạn, ôn tập bất cứ lúc nào, truy cập vĩnh viễn', value: '500.000đ', color: '#00ff88' },
              { icon: '⚙️', title: 'Checklist Triển Khai 30 Ngày', desc: 'Lộ trình hành động cụ thể từng ngày để có AI Agent đầu tiên hoạt động trong 1 tháng', value: '200.000đ', color: '#ff6b35' },
              { icon: '🔑', title: 'Kho 100+ Tools AI Miễn Phí', desc: 'Danh sách tools AI được Tú kiểm duyệt, phân loại theo use case và cập nhật liên tục', value: '300.000đ', color: '#00d4ff' },
            ].map(({ icon, title, desc, value, color }) => (
              <div key={title} style={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: '14px', padding: '22px', transition: 'border-color 0.2s' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
                  <div style={{ fontSize: '32px' }}>{icon}</div>
                  <div style={{ fontSize: '12px', fontWeight: 700, color: 'var(--text-dim)', textDecoration: 'line-through' }}>{value}</div>
                </div>
                <div style={{ fontSize: '15px', fontWeight: 700, color: 'var(--text)', marginBottom: '8px' }}>{title}</div>
                <p style={{ fontSize: '13px', color: 'var(--text-muted)', lineHeight: 1.7 }}>{desc}</p>
                <div style={{ marginTop: '12px', fontSize: '12px', fontWeight: 700, color, background: `${color}12`, border: `1px solid ${color}25`, borderRadius: '6px', padding: '3px 8px', display: 'inline-block' }}>MIỄN PHÍ ✓</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── INSTRUCTOR ──────────────────────────────────────── */}
      <section style={{ padding: '72px 24px', maxWidth: '860px', margin: '0 auto' }}>
        <div style={{ textAlign: 'center', marginBottom: '48px' }}>
          <div style={{ fontSize: '12px', fontWeight: 700, color: 'var(--neon)', textTransform: 'uppercase', letterSpacing: '1.5px', marginBottom: '10px' }}>Diễn giả</div>
          <h2 style={{ fontSize: 'clamp(24px, 3.5vw, 40px)', fontWeight: 800, color: 'var(--text)' }}>Ai Sẽ Training Cho Bạn?</h2>
        </div>
        <div style={{ display: 'flex', gap: '40px', alignItems: 'center', background: 'var(--bg-card)', border: '1px solid var(--border-bright)', borderRadius: '20px', padding: '40px', flexWrap: 'wrap' }}>
          {/* avatar */}
          <div style={{ flexShrink: 0, textAlign: 'center' }}>
            <div style={{ width: '140px', height: '140px', borderRadius: '50%', background: 'linear-gradient(135deg, #00d4ff, #7b2fff)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '52px', fontWeight: 900, color: '#070b14', margin: '0 auto 12px', boxShadow: '0 0 40px rgba(0,212,255,0.3)' }}>
              TÚ
            </div>
            <div style={{ fontSize: '18px', fontWeight: 800, color: 'var(--text)' }}>Tú Marketing</div>
            <div style={{ fontSize: '13px', color: 'var(--neon)', marginTop: '4px' }}>AI Agent & Marketing Expert</div>
          </div>
          {/* bio */}
          <div style={{ flex: 1, minWidth: '280px' }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {[
                { icon: '🏆', text: '14+ năm kinh nghiệm trong ngành Marketing & Sales' },
                { icon: '🤖', text: '3+ năm nghiên cứu và ứng dụng AI vào kinh doanh thực chiến' },
                { icon: '👥', text: 'Đã đào tạo 5.000+ học viên, đồng hành 300+ doanh nghiệp' },
                { icon: '💰', text: 'Xây dựng hệ thống AI Agent giúp KH tiết kiệm 70% chi phí vận hành' },
                { icon: '📢', text: 'Diễn giả tại các sự kiện: Startup Vietnam, Digital Marketing Summit' },
              ].map(({ icon, text }) => (
                <div key={text} style={{ display: 'flex', gap: '10px', alignItems: 'flex-start', fontSize: '15px', color: 'var(--text-muted)' }}>
                  <span style={{ flexShrink: 0, fontSize: '16px' }}>{icon}</span>
                  <span style={{ lineHeight: 1.6 }}>{text}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ── TESTIMONIALS ────────────────────────────────────── */}
      <section style={{ padding: '72px 24px', background: '#0a0f1e' }}>
        <div style={{ maxWidth: '1100px', margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: '48px' }}>
            <div style={{ fontSize: '12px', fontWeight: 700, color: 'var(--neon)', textTransform: 'uppercase', letterSpacing: '1.5px', marginBottom: '10px' }}>Học viên nói gì</div>
            <h2 style={{ fontSize: 'clamp(24px, 3.5vw, 42px)', fontWeight: 800, color: 'var(--text)' }}>
              Kết Quả Thực Tế Từ <span style={{ background: 'linear-gradient(135deg, #00d4ff, #7b2fff)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>Cộng Đồng Tú Marketing</span>
            </h2>
          </div>
          <div className="grid-3" style={{ gap: '20px' }}>
            {[
              { name: 'Nguyễn Văn Đức', role: 'Chủ chuỗi Spa — TP.HCM', avatar: 'ĐỨC', color: '#00d4ff', result: 'Tăng 280% lead/tháng', quote: 'Sau buổi training, tôi setup AI Agent chăm sóc khách hàng tự động. Giờ không cần thuê thêm nhân viên CSKH mà vẫn handle được 500 tin nhắn/ngày. Doanh thu tăng 3x sau 60 ngày.' },
              { name: 'Trần Thị Minh Châu', role: 'Freelancer — Hà Nội', avatar: 'CHÂU', color: '#7b2fff', result: 'Thu nhập 80tr/tháng', quote: 'Tú dạy rất dễ hiểu, tôi mới bắt đầu từ zero mà giờ đã cung cấp dịch vụ AI Agent cho 12 khách hàng. Mỗi tháng thu nhập ổn định 80 triệu từ nguồn này.' },
              { name: 'Lê Hoàng Minh', role: 'CEO Agency Digital — Đà Nẵng', avatar: 'MINH', color: '#00ff88', result: 'Tiết kiệm 70% chi phí', quote: 'Trước đây agency tôi có 15 nhân viên thực hiện công việc manual. Sau khi áp dụng AI Agent theo hướng dẫn của Tú, giờ chỉ cần 8 người mà hiệu suất tăng gấp đôi.' },
            ].map((t) => (
              <div key={t.name} style={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: '16px', padding: '28px', position: 'relative' }}>
                <div style={{ display: 'inline-block', background: `${t.color}15`, border: `1px solid ${t.color}30`, borderRadius: '8px', padding: '4px 12px', fontSize: '12px', fontWeight: 700, color: t.color, marginBottom: '16px' }}>
                  🎯 {t.result}
                </div>
                <div style={{ display: 'flex', gap: '2px', marginBottom: '12px' }}>
                  {[1,2,3,4,5].map(s => <span key={s} style={{ color: '#ffd32a' }}>★</span>)}
                </div>
                <p style={{ fontSize: '14px', color: 'var(--text-muted)', lineHeight: 1.8, marginBottom: '20px', fontStyle: 'italic' }}>
                  &ldquo;{t.quote}&rdquo;
                </p>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', paddingTop: '16px', borderTop: '1px solid var(--border)' }}>
                  <div style={{ width: '42px', height: '42px', borderRadius: '50%', background: `linear-gradient(135deg, ${t.color}, ${t.color}70)`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '11px', fontWeight: 800, color: '#070b14', flexShrink: 0, boxShadow: `0 0 12px ${t.color}40` }}>
                    {t.avatar}
                  </div>
                  <div>
                    <div style={{ fontSize: '14px', fontWeight: 700, color: 'var(--text)' }}>{t.name}</div>
                    <div style={{ fontSize: '12px', color: t.color, marginTop: '2px' }}>{t.role}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── MID-PAGE CTA ────────────────────────────────────── */}
      <div style={{ padding: '48px 24px', textAlign: 'center', background: 'linear-gradient(135deg, rgba(0,212,255,0.06), rgba(123,47,255,0.06))', borderTop: '1px solid var(--border)', borderBottom: '1px solid var(--border)' }}>
        <p style={{ fontSize: '22px', fontWeight: 800, color: 'var(--text)', marginBottom: '8px' }}>
          🔥 Còn <strong style={{ color: '#ffd32a' }}>47 suất</strong> đăng ký miễn phí — Đừng bỏ lỡ!
        </p>
        <p style={{ color: 'var(--text-muted)', marginBottom: '24px', fontSize: '15px' }}>Mỗi ngày có thêm người đăng ký. Số suất có hạn.</p>
        <a href="#dang-ky" className="btn btn-primary btn-xl">🚀 ĐĂNG KÝ NGAY — MIỄN PHÍ →</a>
      </div>

      {/* ── FAQ ─────────────────────────────────────────────── */}
      <section style={{ padding: '72px 24px', maxWidth: '760px', margin: '0 auto' }}>
        <div style={{ textAlign: 'center', marginBottom: '48px' }}>
          <h2 style={{ fontSize: 'clamp(24px, 3vw, 38px)', fontWeight: 800, color: 'var(--text)' }}>Câu Hỏi Thường Gặp</h2>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {[
            { q: 'Workshop này có thực sự miễn phí không?', a: 'Có, 100% miễn phí. Không có phí ẩn hay điều kiện gì. Bạn chỉ cần đăng ký, tham gia và học.' },
            { q: 'Tôi không biết gì về AI Agent, có học được không?', a: 'Hoàn toàn có thể! Workshop được thiết kế cho người mới từ zero. Tú sẽ giải thích từ căn bản nhất. Bạn chỉ cần có máy tính và kết nối internet.' },
            { q: 'Workshop diễn ra ở đâu?', a: 'Online 100% qua Zoom. Sau khi đăng ký, bạn sẽ nhận link phòng Zoom qua email và Zalo trước buổi training 24 giờ.' },
            { q: 'Nếu tôi không tham dự trực tiếp được thì sao?', a: 'Đừng lo! Toàn bộ buổi training sẽ được ghi lại và gửi cho những ai đã đăng ký. Bạn có thể xem lại bất kỳ lúc nào.' },
            { q: 'Sau workshop tôi sẽ làm được gì?', a: 'Bạn sẽ hiểu rõ AI Agent là gì, biết cách build 1 AI Agent cơ bản, và có lộ trình rõ ràng để triển khai vào kinh doanh trong 30 ngày tiếp theo.' },
          ].map(({ q, a }) => (
            <div key={q} style={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: '12px', padding: '20px 22px' }}>
              <div style={{ fontSize: '15px', fontWeight: 700, color: 'var(--neon)', marginBottom: '8px' }}>❓ {q}</div>
              <div style={{ fontSize: '14px', color: 'var(--text-muted)', lineHeight: 1.75 }}>→ {a}</div>
            </div>
          ))}
        </div>
      </section>

      {/* ── REGISTRATION FORM ───────────────────────────────── */}
      <section id="dang-ky" style={{
        padding: '80px 24px',
        background: 'radial-gradient(ellipse 80% 60% at 50% 50%, rgba(0,212,255,0.08) 0%, rgba(123,47,255,0.05) 40%, transparent 70%), #070b14',
        borderTop: '1px solid var(--border)',
      }}>
        <div style={{ maxWidth: '560px', margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: '36px' }}>
            <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', background: 'rgba(0,255,136,0.08)', border: '1px solid rgba(0,255,136,0.25)', borderRadius: '100px', padding: '7px 18px', fontSize: '13px', color: 'var(--neon-green)', marginBottom: '20px', fontWeight: 600 }}>
              🎉 Đăng ký miễn phí — Còn 47 suất
            </div>
            <h2 style={{ fontSize: 'clamp(24px, 3.5vw, 38px)', fontWeight: 900, color: 'var(--text)', letterSpacing: '-0.5px', marginBottom: '12px', lineHeight: 1.2 }}>
              Đăng Ký Tham Gia<br />
              <span style={{ background: 'linear-gradient(135deg, #00d4ff, #7b2fff)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>Workshop AI Agent Ngay!</span>
            </h2>
            <p style={{ color: 'var(--text-muted)', fontSize: '15px', lineHeight: 1.7 }}>
              Điền thông tin bên dưới → Nhận link Zalo VIP ngay lập tức<br />
              <strong style={{ color: 'var(--text)' }}>+ Trọn bộ tài liệu miễn phí trị giá 3.000.000đ</strong>
            </p>
          </div>
          <div style={{ background: 'var(--bg-elevated)', border: '1px solid var(--border-bright)', borderRadius: '20px', padding: '36px', boxShadow: '0 20px 60px rgba(0,0,0,0.5), 0 0 40px rgba(0,212,255,0.06)' }}>
            <LandingForm />
          </div>
        </div>
      </section>

      {/* ── FOOTER ──────────────────────────────────────────── */}
      <footer style={{ background: '#05080f', borderTop: '1px solid var(--border)', padding: '32px 24px', textAlign: 'center' }}>
        <div style={{ fontSize: '20px', fontWeight: 900, background: 'linear-gradient(135deg, #00d4ff, #7b2fff)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text', marginBottom: '12px' }}>
          Tú Marketing
        </div>
        <p style={{ fontSize: '14px', color: 'var(--text-muted)', maxWidth: '400px', margin: '0 auto 16px', lineHeight: 1.7 }}>
          Đào tạo AI Agent & Marketing Automation thực chiến hàng đầu Việt Nam
        </p>
        <div style={{ display: 'flex', gap: '24px', justifyContent: 'center', flexWrap: 'wrap', fontSize: '13px', color: 'var(--text-dim)', marginBottom: '20px' }}>
          <Link href="/courses" style={{ color: 'var(--text-muted)', textDecoration: 'none' }}>Khóa học</Link>
          <Link href="/blog" style={{ color: 'var(--text-muted)', textDecoration: 'none' }}>Blog</Link>
          <Link href="/login" style={{ color: 'var(--text-muted)', textDecoration: 'none' }}>Đăng nhập</Link>
          <Link href="/chinh-sach-bao-mat" style={{ color: 'var(--text-muted)', textDecoration: 'none' }}>Chính sách bảo mật</Link>
        </div>
        <div style={{ fontSize: '13px', color: 'var(--text-dim)', borderTop: '1px solid var(--border)', paddingTop: '20px' }}>
          © {new Date().getFullYear()} Tú Marketing. Bảo lưu mọi quyền. &nbsp;|&nbsp; Hotline: <a href="tel:0909123456" style={{ color: 'var(--neon)', textDecoration: 'none' }}>0909 123 456</a>
        </div>
      </footer>

    </div>
  )
}

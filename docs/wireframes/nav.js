function buildNav(active, loggedIn) {
  const pages = [
    { href: 'index.html', label: 'Trang chủ' },
    { href: 'courses.html', label: 'Khóa học' },
    { href: 'blog.html', label: 'Blog' },
  ];
  const links = pages.map(p =>
    `<a href="${p.href}" class="${active === p.href ? 'active' : ''}">${p.label}</a>`
  ).join('');

  const right = loggedIn
    ? `<div class="nav-avatar-menu">
        <div class="nav-avatar">AN</div>
        <div class="avatar-dropdown">
          <a href="dashboard.html">📚 Khóa học của tôi</a>
          <a href="dashboard-affiliate.html">💰 Affiliate</a>
          <a href="dashboard-profile.html">👤 Hồ sơ</a>
          <a href="admin-dashboard.html">⚙️ Quản trị</a>
          <hr style="border:none;border-top:1px solid #eee">
          <a href="login.html">Đăng xuất</a>
        </div>
      </div>`
    : `<a href="login.html" class="btn-ghost btn-sm">Đăng nhập</a>
       <a href="register.html" class="btn-primary btn-sm">Đăng ký</a>`;

  const mobileLinks = pages.map(p =>
    `<a href="${p.href}">${p.label}</a>`
  ).join('') + (loggedIn
    ? `<a href="dashboard.html">Khóa học của tôi</a>
       <a href="dashboard-affiliate.html">Affiliate</a>
       <a href="admin-dashboard.html">Quản trị</a>
       <a href="login.html">Đăng xuất</a>`
    : `<a href="login.html">Đăng nhập</a><a href="register.html">Đăng ký miễn phí</a>`);

  document.getElementById('nav-placeholder').innerHTML = `
    <nav class="nav">
      <a href="index.html" class="nav-logo">EduViet<span style="font-weight:400">Pro</span></a>
      <div class="nav-links">${links}</div>
      <div class="nav-right">${right}</div>
      <div class="hamburger" onclick="toggleMobileMenu()">
        <span></span><span></span><span></span>
      </div>
    </nav>
    <div class="mobile-menu" id="mobile-menu">${mobileLinks}</div>`;
}

function toggleMobileMenu() {
  document.getElementById('mobile-menu').classList.toggle('open');
}

import type { Metadata } from 'next'
import './globals.css'
import { AuthProvider } from '@/lib/auth'

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || 'https://tumarketing.vn'
const SITE_NAME = 'Tú Marketing'
const DEFAULT_DESC = 'Đào tạo AI Agent & Marketing Automation thực chiến hàng đầu Việt Nam. Tham gia workshop miễn phí cùng Tú Marketing.'

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: { default: `${SITE_NAME} — AI Agent & Marketing Automation`, template: `%s | ${SITE_NAME}` },
  description: DEFAULT_DESC,
  openGraph: {
    type: 'website',
    siteName: SITE_NAME,
    title: `${SITE_NAME} — AI Agent & Marketing Automation`,
    description: DEFAULT_DESC,
    url: SITE_URL,
    locale: 'vi_VN',
  },
  twitter: {
    card: 'summary_large_image',
    site: '@tumarketing',
    title: `${SITE_NAME} — AI Agent & Marketing Automation`,
    description: DEFAULT_DESC,
  },
  robots: {
    index: true,
    follow: true,
    googleBot: { index: true, follow: true, 'max-snippet': -1, 'max-image-preview': 'large', 'max-video-preview': -1 },
  },
  alternates: {
    canonical: SITE_URL,
  },
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="vi">
      <body>
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  )
}

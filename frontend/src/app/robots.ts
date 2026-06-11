import type { MetadataRoute } from 'next'

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || 'https://tumarketing.vn'

export default function robots(): MetadataRoute.Robots {
  return {
    rules: [
      {
        userAgent: '*',
        allow: ['/', '/courses', '/courses/', '/blog', '/blog/', '/login', '/register', '/chinh-sach-bao-mat', '/dieu-khoan'],
        disallow: ['/admin', '/admin/', '/dashboard', '/dashboard/', '/learn', '/learn/', '/api', '/api/'],
      },
    ],
    sitemap: `${SITE_URL}/sitemap.xml`,
  }
}

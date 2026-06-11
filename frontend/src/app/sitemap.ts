import type { MetadataRoute } from 'next'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || 'https://tumarketing.vn'

async function getCourseSlugs(): Promise<string[]> {
  try {
    const res = await fetch(`${API_URL}/api/courses?page=1&page_size=200`, {
      next: { revalidate: 3600 },
    })
    if (!res.ok) return []
    const data = await res.json()
    const items = data.items ?? data ?? []
    return items.map((c: { slug: string }) => c.slug).filter(Boolean)
  } catch {
    return []
  }
}

async function getBlogSlugs(): Promise<string[]> {
  try {
    const res = await fetch(`${API_URL}/api/blog/posts?page=1&page_size=200`, {
      next: { revalidate: 3600 },
    })
    if (!res.ok) return []
    const data = await res.json()
    const items = data.items ?? data ?? []
    return items.map((p: { slug: string }) => p.slug).filter(Boolean)
  } catch {
    return []
  }
}

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const [courseSlugs, blogSlugs] = await Promise.all([getCourseSlugs(), getBlogSlugs()])

  const staticPages: MetadataRoute.Sitemap = [
    { url: `${SITE_URL}/`, lastModified: new Date(), changeFrequency: 'weekly', priority: 1.0 },
    { url: `${SITE_URL}/courses`, lastModified: new Date(), changeFrequency: 'daily', priority: 0.9 },
    { url: `${SITE_URL}/blog`, lastModified: new Date(), changeFrequency: 'daily', priority: 0.8 },
    { url: `${SITE_URL}/chinh-sach-bao-mat`, lastModified: new Date(), changeFrequency: 'yearly', priority: 0.3 },
    { url: `${SITE_URL}/dieu-khoan`, lastModified: new Date(), changeFrequency: 'yearly', priority: 0.3 },
  ]

  const coursePages: MetadataRoute.Sitemap = courseSlugs.map(slug => ({
    url: `${SITE_URL}/courses/${slug}`,
    lastModified: new Date(),
    changeFrequency: 'weekly' as const,
    priority: 0.85,
  }))

  const blogPages: MetadataRoute.Sitemap = blogSlugs.map(slug => ({
    url: `${SITE_URL}/blog/${slug}`,
    lastModified: new Date(),
    changeFrequency: 'monthly' as const,
    priority: 0.7,
  }))

  return [...staticPages, ...coursePages, ...blogPages]
}

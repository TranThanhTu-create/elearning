import type { Metadata } from 'next'
import { notFound } from 'next/navigation'
import Link from 'next/link'
import Navbar from '@/components/layout/Navbar'
import Footer from '@/components/layout/Footer'
import BlogCard from '@/components/features/BlogCard'
import { formatDate } from '@/lib/utils'
import type { BlogPost } from '@/types'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || 'https://tumarketing.vn'

type Props = { params: Promise<{ slug: string }> }

async function getPost(slug: string): Promise<BlogPost | null> {
  try {
    const res = await fetch(`${API_URL}/api/blog/posts/${slug}`, {
      next: { revalidate: 60 },
    })
    if (!res.ok) return null
    return res.json()
  } catch {
    return null
  }
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params
  const post = await getPost(slug)
  if (!post) return { title: 'Không tìm thấy bài viết' }

  const description = post.excerpt || post.content?.replace(/<[^>]+>/g, '').slice(0, 160) || ''
  const ogImage = post.thumbnail_url
    ? [{ url: post.thumbnail_url, width: 1200, height: 630, alt: post.title }]
    : []

  return {
    title: post.title,
    description,
    openGraph: {
      title: post.title,
      description,
      url: `${SITE_URL}/blog/${post.slug}`,
      type: 'article',
      images: ogImage,
      ...(post.published_at && { publishedTime: post.published_at }),
      ...(post.author_name && { authors: [post.author_name] }),
    },
    twitter: {
      card: 'summary_large_image',
      title: post.title,
      description,
      images: post.thumbnail_url ? [post.thumbnail_url] : [],
    },
    alternates: {
      canonical: `${SITE_URL}/blog/${post.slug}`,
    },
  }
}

export default async function BlogPostPage({ params }: Props) {
  const { slug } = await params
  const post = await getPost(slug)
  if (!post) notFound()

  const description = post.excerpt || post.content?.replace(/<[^>]+>/g, '').slice(0, 160) || ''

  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'Article',
    headline: post.title,
    description,
    image: post.thumbnail_url || '',
    url: `${SITE_URL}/blog/${post.slug}`,
    datePublished: post.published_at || post.created_at || '',
    dateModified: post.published_at || post.created_at || '',
    author: {
      '@type': 'Person',
      name: post.author_name || 'Tú Marketing',
    },
    publisher: {
      '@type': 'Organization',
      name: 'Tú Marketing',
      logo: {
        '@type': 'ImageObject',
        url: `${SITE_URL}/logo.png`,
      },
    },
    ...(post.tags && post.tags.length > 0 && {
      keywords: post.tags.map(t => t.name).join(', '),
    }),
  }

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <Navbar />
      <main>
        <article>
          {/* Header */}
          <div style={{ background: '#111', color: '#fff', padding: '48px 0' }}>
            <div className="container" style={{ maxWidth: '720px' }}>
              {post.category && (
                <div style={{ marginBottom: '12px' }}>
                  <Link href={`/blog?category=${post.category.slug}`} style={{ fontSize: '13px', color: '#aaa', textDecoration: 'none', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                    {post.category.name}
                  </Link>
                </div>
              )}
              <h1 style={{ fontSize: '32px', fontWeight: 800, lineHeight: 1.3, marginBottom: '16px' }}>{post.title}</h1>
              <div style={{ display: 'flex', gap: '16px', fontSize: '14px', color: '#aaa', flexWrap: 'wrap' }}>
                {post.author_name && <span>✍️ {post.author_name}</span>}
                {post.published_at && <span>📅 {formatDate(post.published_at)}</span>}
                {post.reading_time && <span>⏱️ {post.reading_time} phút đọc</span>}
              </div>
            </div>
          </div>

          {/* Thumbnail */}
          {post.thumbnail_url && (
            <div className="container" style={{ maxWidth: '720px' }}>
              <img src={post.thumbnail_url} alt={post.title} style={{ width: '100%', aspectRatio: '16/9', objectFit: 'cover', borderRadius: '8px', marginTop: '-24px', boxShadow: '0 8px 32px rgba(0,0,0,.15)' }} />
            </div>
          )}

          {/* Content */}
          <div className="container section-sm" style={{ maxWidth: '720px' }}>
            {post.content && (
              <div
                style={{ fontSize: '16px', lineHeight: 1.8, color: '#333' }}
                dangerouslySetInnerHTML={{ __html: post.content }}
              />
            )}

            {/* Tags */}
            {post.tags && post.tags.length > 0 && (
              <div style={{ marginTop: '32px', paddingTop: '24px', borderTop: '1px solid #eee', display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                {post.tags.map(t => (
                  <span key={t.slug} className="tag tag-default">#{t.name}</span>
                ))}
              </div>
            )}
          </div>
        </article>

        {/* Related posts */}
        {post.related_posts && post.related_posts.length > 0 && (
          <div className="section" style={{ background: '#f6f6f6' }}>
            <div className="container">
              <h2 className="section-title">Bài viết liên quan</h2>
              <div className="grid-3">
                {post.related_posts.map(p => <BlogCard key={p.id} post={p} />)}
              </div>
            </div>
          </div>
        )}
      </main>
      <Footer />
    </>
  )
}

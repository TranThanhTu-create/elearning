import Link from 'next/link'
import type { BlogPost } from '@/types'
import { formatDate } from '@/lib/utils'

interface Props {
  post: BlogPost
}

export default function BlogCard({ post }: Props) {
  return (
    <Link href={`/blog/${post.slug}`} className="blog-card">
      <div className="blog-thumb">
        {post.thumbnail_url
          ? <img src={post.thumbnail_url} alt={post.title} loading="lazy" />
          : <div style={{ width: '100%', height: '100%', background: 'linear-gradient(135deg, #e8e8e8, #d0d0d0)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '40px' }}>✍️</div>
        }
      </div>
      <div className="blog-body">
        {post.category && <div className="blog-cat">{post.category.name}</div>}
        <div className="blog-title">{post.title}</div>
        {post.excerpt && <div className="blog-excerpt">{post.excerpt}</div>}
        <div className="blog-meta">
          {post.author_name && <span>{post.author_name} · </span>}
          {post.published_at && <span>{formatDate(post.published_at)}</span>}
          {post.reading_time && <span> · {post.reading_time} phút đọc</span>}
        </div>
      </div>
    </Link>
  )
}

import Link from 'next/link'
import type { Course } from '@/types'
import { formatVnd, formatNumber } from '@/lib/utils'

interface Props {
  course: Course
}

export default function CourseCard({ course }: Props) {
  return (
    <Link href={`/courses/${course.slug}`} className="course-card">
      <div className="course-thumb">
        {course.thumbnail_url
          ? <img src={course.thumbnail_url} alt={course.title} loading="lazy" />
          : <div style={{ width: '100%', height: '100%', background: 'linear-gradient(135deg, #e8e8e8, #d0d0d0)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '40px' }}>🎓</div>
        }
        {course.discount_percent && course.discount_percent > 0 ? (
          <div style={{ position: 'absolute', top: 10, left: 10, background: '#cc0000', color: '#fff', fontSize: '12px', fontWeight: 700, padding: '3px 8px', borderRadius: '4px' }}>
            -{course.discount_percent}%
          </div>
        ) : null}
      </div>
      <div className="course-body">
        {course.category && (
          <div className="course-badge">{course.category.name}</div>
        )}
        <div className="course-title">{course.title}</div>
        <div className="course-meta">
          {course.total_lessons != null && <span>{course.total_lessons} bài học</span>}
          {course.level && <span>{levelLabel(course.level)}</span>}
        </div>
        <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px' }}>
          <span className="course-price">
            {course.price === 0 ? 'Miễn phí' : formatVnd(course.price)}
          </span>
          {course.original_price && course.original_price > course.price && (
            <span className="course-price-old">{formatVnd(course.original_price)}</span>
          )}
        </div>
        <div className="course-footer">
          <span>⭐ {course.avg_rating.toFixed(1)}</span>
          <span>{formatNumber(course.total_students)} học viên</span>
        </div>
      </div>
    </Link>
  )
}

function levelLabel(level: string): string {
  return { beginner: 'Cơ bản', intermediate: 'Trung cấp', advanced: 'Nâng cao' }[level] ?? level
}

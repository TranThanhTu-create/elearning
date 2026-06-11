'use client'

import { useState } from 'react'
import { formatDuration } from '@/lib/utils'
import type { Chapter } from '@/types'

interface Props {
  chapters: Chapter[]
  defaultOpenId: string | null
}

export default function CourseAccordion({ chapters, defaultOpenId }: Props) {
  const [openChapter, setOpenChapter] = useState<string | null>(defaultOpenId)

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
      {chapters.map(chapter => (
        <div key={chapter.id} style={{ border: '1px solid var(--border)', borderRadius: '10px', overflow: 'hidden' }}>
          <button
            style={{
              width: '100%', padding: '13px 16px',
              background: openChapter === chapter.id ? 'rgba(0,212,255,0.06)' : 'var(--bg-elevated)',
              border: 'none', cursor: 'pointer',
              display: 'flex', justifyContent: 'space-between', alignItems: 'center',
              fontFamily: 'inherit', fontWeight: 600, fontSize: '14px',
              textAlign: 'left', color: 'var(--text)', transition: 'background 0.15s',
            }}
            onClick={() => setOpenChapter(openChapter === chapter.id ? null : chapter.id)}
          >
            <span>{chapter.title}</span>
            <span style={{ color: 'var(--text-muted)', fontWeight: 400, fontSize: '13px', whiteSpace: 'nowrap', marginLeft: '8px' }}>
              {chapter.lessons?.length || 0} bài {openChapter === chapter.id ? '▲' : '▼'}
            </span>
          </button>
          {openChapter === chapter.id && (
            <div>
              {chapter.lessons?.map((lesson, i) => (
                <div key={lesson.id} style={{
                  padding: '10px 16px', display: 'flex', alignItems: 'center', gap: '8px',
                  borderTop: '1px solid var(--border)', fontSize: '14px',
                  background: i % 2 === 0 ? 'transparent' : 'rgba(255,255,255,0.01)',
                }}>
                  <span style={{ fontSize: '13px' }}>{lesson.is_preview ? '▶️' : '🔒'}</span>
                  <span style={{ flex: 1, color: 'var(--text-muted)' }}>{lesson.title}</span>
                  {lesson.duration_seconds && (
                    <span style={{ color: 'var(--text-dim)', fontSize: '12px' }}>
                      {formatDuration(lesson.duration_seconds)}
                    </span>
                  )}
                  {lesson.is_preview && (
                    <span style={{ fontSize: '11px', background: 'rgba(0,255,136,0.1)', color: 'var(--neon-green)', border: '1px solid rgba(0,255,136,0.2)', padding: '2px 6px', borderRadius: '4px', fontWeight: 600 }}>
                      Xem thử
                    </span>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  )
}

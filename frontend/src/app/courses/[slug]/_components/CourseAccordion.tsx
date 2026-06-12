'use client'

import { useState } from 'react'
import type { Chapter } from '@/types'

interface Props {
  chapters: Chapter[]
}

function fmtDuration(s: number) {
  if (!s) return ''
  const m = Math.floor(s / 60), sec = s % 60
  return `${m}:${sec.toString().padStart(2, '0')}`
}

export default function CourseAccordion({ chapters }: Props) {
  const [open, setOpen] = useState<string | null>(chapters[0]?.id ?? null)
  const [playing, setPlaying] = useState<string | null>(null)

  const totalLessons = chapters.reduce((s, c) => s + (c.lessons?.length || 0), 0)

  return (
    <div>
      <div style={{ display: 'flex', gap: '16px', fontSize: '13px', color: 'var(--text-muted)', marginBottom: '16px', flexWrap: 'wrap' }}>
        <span>{chapters.length} chương</span>
        <span>·</span>
        <span>{totalLessons} bài học</span>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
        {chapters.map((chapter, ci) => {
          const isOpen = open === chapter.id
          const chapterDuration = chapter.lessons?.reduce((s, l) => s + (l.duration_seconds || 0), 0) || 0

          return (
            <div key={chapter.id} style={{ border: '1px solid var(--border)', borderRadius: '10px', overflow: 'hidden' }}>
              {/* Chapter header */}
              <button
                onClick={() => setOpen(isOpen ? null : chapter.id)}
                style={{
                  width: '100%', padding: '14px 16px',
                  background: isOpen ? 'rgba(0,212,255,0.06)' : 'var(--bg-elevated)',
                  border: 'none', cursor: 'pointer',
                  display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                  fontFamily: 'inherit', textAlign: 'left', color: 'var(--text)',
                  transition: 'background 0.15s',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <span style={{
                    width: '24px', height: '24px', borderRadius: '50%',
                    background: isOpen ? 'var(--neon)' : 'rgba(255,255,255,0.08)',
                    color: isOpen ? '#000' : 'var(--text-muted)',
                    fontSize: '11px', fontWeight: 700,
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    flexShrink: 0,
                  }}>{ci + 1}</span>
                  <span style={{ fontWeight: 600, fontSize: '14px' }}>{chapter.title}</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexShrink: 0 }}>
                  <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                    {chapter.lessons?.length || 0} bài
                    {chapterDuration > 0 && ` · ${fmtDuration(chapterDuration)}`}
                  </span>
                  <span style={{ fontSize: '12px', color: 'var(--text-muted)', transition: 'transform 0.2s', display: 'inline-block', transform: isOpen ? 'rotate(180deg)' : 'none' }}>▼</span>
                </div>
              </button>

              {/* Lessons list */}
              {isOpen && (
                <div>
                  {chapter.lessons?.map((lesson, li) => {
                    const isFree = lesson.is_free ?? lesson.is_preview ?? false
                    const videoId = lesson.video_id
                    const isPlaying = playing === lesson.id
                    const hasVideo = isFree && !!videoId

                    return (
                      <div key={lesson.id}>
                        {/* Lesson row */}
                        <div
                          onClick={() => hasVideo && setPlaying(isPlaying ? null : lesson.id)}
                          style={{
                            padding: '10px 16px',
                            display: 'flex', alignItems: 'center', gap: '10px',
                            borderTop: '1px solid var(--border)',
                            fontSize: '13px',
                            cursor: hasVideo ? 'pointer' : 'default',
                            background: isPlaying ? 'rgba(0,212,255,0.06)' : 'transparent',
                            transition: 'background 0.15s',
                          }}
                        >
                          {/* Icon */}
                          <span style={{
                            width: '28px', height: '28px', borderRadius: '50%', flexShrink: 0,
                            border: `1px solid ${isFree ? 'rgba(0,255,136,0.3)' : 'var(--border)'}`,
                            background: isFree ? 'rgba(0,255,136,0.06)' : 'transparent',
                            display: 'flex', alignItems: 'center', justifyContent: 'center',
                            fontSize: '11px',
                          }}>
                            {isPlaying ? '⏸' : isFree ? '▶' : '🔒'}
                          </span>

                          {/* Index */}
                          <span style={{ color: 'var(--text-dim)', fontSize: '11px', flexShrink: 0, width: '20px' }}>
                            {String(li + 1).padStart(2, '0')}
                          </span>

                          {/* Title */}
                          <span style={{
                            flex: 1, color: isFree ? 'var(--text)' : 'var(--text-muted)',
                            overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
                          }}>
                            {lesson.title}
                          </span>

                          {/* Badges + duration */}
                          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexShrink: 0 }}>
                            {isFree && (
                              <span style={{
                                fontSize: '10px', fontWeight: 700, padding: '2px 7px', borderRadius: '4px',
                                background: 'rgba(0,255,136,0.12)', color: '#00ff88',
                                border: '1px solid rgba(0,255,136,0.25)',
                              }}>MIỄN PHÍ</span>
                            )}
                            {lesson.duration_seconds && lesson.duration_seconds > 0 && (
                              <span style={{ fontSize: '11px', color: 'var(--text-dim)' }}>
                                {lesson.duration_fmt || fmtDuration(lesson.duration_seconds)}
                              </span>
                            )}
                          </div>
                        </div>

                        {/* Inline YouTube player */}
                        {isPlaying && videoId && (
                          <div style={{ padding: '0 16px 16px', borderTop: '1px solid var(--border)', background: 'rgba(0,212,255,0.03)' }}>
                            <div style={{ position: 'relative', paddingBottom: '56.25%', borderRadius: '10px', overflow: 'hidden', marginTop: '12px' }}>
                              <iframe
                                src={`https://www.youtube.com/embed/${videoId}?autoplay=1&rel=0`}
                                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                                allowFullScreen
                                style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', border: 'none' }}
                              />
                            </div>
                          </div>
                        )}
                      </div>
                    )
                  })}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}

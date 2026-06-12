'use client'

import { useRef, useState, DragEvent } from 'react'
import { api } from '@/lib/api'

interface Props {
  value: string
  onChange: (url: string) => void
  label?: string
  aspectRatio?: string  // e.g. "16/9"
}

export default function ImageUploader({ value, onChange, label = 'Ảnh', aspectRatio = '16/9' }: Props) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState('')
  const [drag, setDrag] = useState(false)
  const [progress, setProgress] = useState(0)

  const upload = async (file: File) => {
    setError('')
    setUploading(true)
    setProgress(0)

    if (!file.type.startsWith('image/')) {
      setError('Chỉ chấp nhận file ảnh (JPG, PNG, WebP, GIF)')
      setUploading(false)
      return
    }
    if (file.size > 10 * 1024 * 1024) {
      setError('File quá lớn. Tối đa 10MB.')
      setUploading(false)
      return
    }

    try {
      const form = new FormData()
      form.append('file', file)

      const { data } = await api.post('/admin/upload/image', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (evt) => {
          if (evt.total) setProgress(Math.round((evt.loaded / evt.total) * 100))
        },
      })
      onChange(data.url)
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Upload thất bại'
      // Extract axios error detail
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const detail = (err as any)?.response?.data?.detail
      setError(detail || msg)
    } finally {
      setUploading(false)
      setProgress(0)
    }
  }

  const onFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0]
    if (f) upload(f)
    e.target.value = ''
  }

  const onDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault(); setDrag(false)
    const f = e.dataTransfer.files?.[0]
    if (f) upload(f)
  }

  return (
    <div className="form-group">
      <label className="form-label">{label}</label>

      {/* Preview / drop zone */}
      <div
        onClick={() => !uploading && inputRef.current?.click()}
        onDragOver={e => { e.preventDefault(); setDrag(true) }}
        onDragLeave={() => setDrag(false)}
        onDrop={onDrop}
        style={{
          border: `2px dashed ${drag ? 'var(--neon)' : value ? 'var(--border-bright)' : 'var(--border)'}`,
          borderRadius: '10px',
          overflow: 'hidden',
          cursor: uploading ? 'default' : 'pointer',
          transition: 'border-color 0.2s, box-shadow 0.2s',
          boxShadow: drag ? '0 0 16px rgba(0,212,255,0.2)' : 'none',
          background: 'var(--bg-elevated)',
          position: 'relative',
        }}
      >
        {value ? (
          <div style={{ position: 'relative' }}>
            <img src={value} alt="preview" style={{ width: '100%', aspectRatio, objectFit: 'cover', display: 'block' }} />
            {/* Overlay on hover */}
            {!uploading && (
              <div style={{
                position: 'absolute', inset: 0,
                background: 'rgba(0,0,0,0.55)',
                display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '8px',
                opacity: 0, transition: 'opacity 0.2s',
              }}
                onMouseOver={e => (e.currentTarget.style.opacity = '1')}
                onMouseOut={e => (e.currentTarget.style.opacity = '0')}
              >
                <span style={{ fontSize: '28px' }}>📷</span>
                <span style={{ color: '#fff', fontSize: '13px', fontWeight: 600 }}>Click hoặc kéo thả để đổi ảnh</span>
              </div>
            )}
          </div>
        ) : (
          <div style={{ padding: '32px 20px', textAlign: 'center' }}>
            <div style={{ fontSize: '36px', marginBottom: '10px' }}>{drag ? '⬇️' : '📁'}</div>
            <div style={{ fontSize: '14px', fontWeight: 600, color: 'var(--text)', marginBottom: '4px' }}>
              {drag ? 'Thả ảnh vào đây' : 'Click để chọn ảnh'}
            </div>
            <div style={{ fontSize: '12px', color: 'var(--text-dim)' }}>
              hoặc kéo thả từ máy tính · JPG, PNG, WebP, GIF · Tối đa 10MB
            </div>
          </div>
        )}

        {/* Upload progress overlay */}
        {uploading && (
          <div style={{
            position: 'absolute', inset: 0,
            background: 'rgba(7,11,20,0.85)',
            display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '12px',
          }}>
            <div style={{ fontSize: '13px', color: 'var(--text)', fontWeight: 600 }}>Đang tải lên… {progress}%</div>
            <div style={{ width: '160px', height: '4px', background: 'rgba(255,255,255,0.1)', borderRadius: '2px', overflow: 'hidden' }}>
              <div style={{ height: '100%', width: `${progress}%`, background: 'var(--neon)', transition: 'width 0.2s', borderRadius: '2px' }} />
            </div>
          </div>
        )}
      </div>

      {/* URL text input fallback */}
      <input
        type="url"
        className="form-input"
        value={value}
        onChange={e => onChange(e.target.value)}
        placeholder="https://... hoặc upload ảnh từ máy tính bên trên"
        style={{ marginTop: '8px', fontSize: '12px' }}
      />

      {/* Actions row */}
      <div style={{ display: 'flex', gap: '8px', marginTop: '8px', alignItems: 'center' }}>
        <button
          type="button"
          className="btn btn-ghost btn-sm"
          onClick={() => inputRef.current?.click()}
          disabled={uploading}
          style={{ fontSize: '12px' }}
        >
          {uploading ? <><span className="spinner" style={{ width: '12px', height: '12px' }} /> Đang tải…</> : '📁 Chọn file từ máy tính'}
        </button>
        {value && (
          <button
            type="button"
            className="btn btn-danger btn-sm"
            onClick={() => onChange('')}
            disabled={uploading}
            style={{ fontSize: '12px' }}
          >
            🗑 Xóa ảnh
          </button>
        )}
      </div>

      {error && (
        <div style={{ marginTop: '6px', fontSize: '12px', color: 'var(--color-danger)', padding: '6px 10px', background: 'rgba(255,71,87,0.08)', borderRadius: '6px', border: '1px solid rgba(255,71,87,0.2)' }}>
          ⚠️ {error}
        </div>
      )}

      <input
        ref={inputRef}
        type="file"
        accept="image/jpeg,image/png,image/webp,image/gif"
        style={{ display: 'none' }}
        onChange={onFileChange}
      />
    </div>
  )
}

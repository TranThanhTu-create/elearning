'use client'

import { useState, useEffect } from 'react'
import { api, extractError } from '@/lib/api'
import type { SiteSetting } from '@/types'

const SECTIONS: Record<string, string> = {
  general: 'Thông tin chung',
  payment: 'Thanh toán (SePay)',
  email: 'Email (Resend)',
  analytics: 'Analytics (GA4/Meta)',
  affiliate: 'Affiliate',
  lead_magnet: 'Lead Magnet',
  integrations: 'Tích hợp (R2, Sheets)',
}

export default function AdminSettingsPage() {
  const [settings, setSettings] = useState<Record<string, SiteSetting[]>>({})
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [activeSection, setActiveSection] = useState('general')

  useEffect(() => {
    api.get('/admin/settings').then(r => {
      const data: SiteSetting[] = r.data
      const grouped: Record<string, SiteSetting[]> = {}
      data.forEach(s => {
        if (!grouped[s.section]) grouped[s.section] = []
        grouped[s.section].push(s)
      })
      setSettings(grouped)
    }).catch(() => {}).finally(() => setLoading(false))
  }, [])

  const updateValue = (section: string, key: string, value: string) => {
    setSettings(prev => ({
      ...prev,
      [section]: (prev[section] || []).map(s => s.key === key ? { ...s, value } : s),
    }))
  }

  const saveSection = async () => {
    setSaving(true)
    setError('')
    setSuccess('')
    try {
      const sectionSettings = settings[activeSection] || []
      const updates = sectionSettings.reduce<Record<string, string>>((acc, s) => { acc[s.key] = s.value; return acc }, {})
      await api.patch('/admin/settings/bulk-update', { section: activeSection, updates })
      setSuccess('Lưu cài đặt thành công!')
    } catch (err) {
      setError(extractError(err))
    } finally {
      setSaving(false)
    }
  }

  if (loading) return <div className="admin-body"><div className="skeleton" style={{ height: '400px' }} /></div>

  const currentSettings = settings[activeSection] || []

  return (
    <>
      <div className="admin-header">
        <h1>Cài đặt hệ thống</h1>
        <button className="btn btn-primary" onClick={saveSection} disabled={saving}>
          {saving ? <span className="spinner" /> : 'Lưu cài đặt'}
        </button>
      </div>
      <div className="admin-body">
        {error && <div className="alert alert-error">{error}</div>}
        {success && <div className="alert alert-success">{success}</div>}

        <div style={{ display: 'flex', gap: '20px', alignItems: 'flex-start' }}>
          {/* Section nav */}
          <div style={{ width: '200px', flexShrink: 0 }}>
            <div className="card" style={{ padding: '8px 0' }}>
              {Object.entries(SECTIONS).map(([key, label]) => (
                <button
                  key={key}
                  onClick={() => setActiveSection(key)}
                  style={{
                    display: 'block', width: '100%', padding: '10px 16px', border: 'none',
                    background: activeSection === key ? '#111' : 'transparent',
                    color: activeSection === key ? '#fff' : '#333',
                    cursor: 'pointer', textAlign: 'left', fontFamily: 'inherit', fontSize: '14px',
                    fontWeight: activeSection === key ? 700 : 400,
                  }}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>

          {/* Settings form */}
          <div style={{ flex: 1 }}>
            <div className="card">
              <h3 style={{ fontWeight: 700, marginBottom: '20px' }}>{SECTIONS[activeSection]}</h3>
              {currentSettings.length === 0 ? (
                <div style={{ color: '#888', textAlign: 'center', padding: '32px' }}>Không có cài đặt cho mục này</div>
              ) : (
                currentSettings.map(s => (
                  <div key={s.key} className="form-group">
                    <label className="form-label">
                      {s.label || s.key}
                      {s.is_secret && <span style={{ fontSize: '11px', color: '#888', marginLeft: '6px' }}>(mật khẩu)</span>}
                    </label>
                    <input
                      className="form-input"
                      type={s.is_secret ? 'password' : 'text'}
                      value={s.value}
                      onChange={e => updateValue(activeSection, s.key, e.target.value)}
                      placeholder={s.is_secret ? '••••••••' : undefined}
                    />
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </>
  )
}

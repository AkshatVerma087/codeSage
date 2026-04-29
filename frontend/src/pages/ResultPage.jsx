import React from 'react'
import { useNavigate } from 'react-router-dom'
import '../App.css'

const ResultPage = () => {
  const navigate = useNavigate()

  return (
    <div style={{ background: 'var(--bg-base)', minHeight: '580px' }}>
      <nav className="navbar">
        <div className="logo">Code<span className="logo-dot">.</span>Sage</div>
        <div className="nav-center">Security analysis · codesage-backend</div>
        <div className="nav-right">
          <div className="avatar">AS</div>
          <button className="btn btn-ghost">Sign out</button>
        </div>
      </nav>

      <div style={{ padding: '16px 28px' }}>
        <div style={{ width: '100%', maxWidth: '1440px', margin: '0 auto' }}>
          <div className="flex items-start justify-between flex-wrap gap-10 mb-20" style={{ flexWrap: 'wrap' }}>
          <div>
            <div className="result-meta">
              <div className="result-heading">Security analysis</div>
              <span className="badge badge-done">Completed</span>
            </div>
            <div className="result-submeta mt-4">
              <span>codesage-backend</span>
              <span className="meta-sep">·</span>
              <span>April 23, 2026 · 14:32</span>
              <span className="meta-sep">·</span>
              <span>2.8s</span>
            </div>
          </div>
          <div className="result-actions">
            <button className="btn btn-secondary" type="button" onClick={() => navigate('/dashboard')}>← Back to dashboard</button>
            <button className="btn btn-primary">Ask follow-up</button>
          </div>
        </div>

        <div className="score-grid">
          <div className="score-card">
            <div className="score-label">Security score</div>
            <div className="score-value" style={{ color: 'var(--status-warn)' }}>6/10</div>
          </div>
          <div className="score-card">
            <div className="score-label">Issues found</div>
            <div className="score-value" style={{ color: 'var(--status-error)' }}>4</div>
          </div>
          <div className="score-card">
            <div className="score-label">Files scanned</div>
            <div className="score-value">142</div>
          </div>
          <div className="score-card">
            <div className="score-label">Critical</div>
            <div className="score-value" style={{ color: 'var(--status-error)' }}>1</div>
          </div>
        </div>

        <div className="summary-card">
          <div className="summary-card-title">Summary</div>
          <div className="summary-body">
            The backend has a solid JWT-based auth foundation, but three security issues were found in the token handling layer. The most critical is a missing secret validation at startup. Rate limiting is partially implemented but not applied to sensitive auth endpoints. Password hashing uses bcrypt correctly (12 rounds).
          </div>
        </div>

        <div className="summary-card">
          <div className="summary-card-title">Findings</div>
          <div className="finding finding-critical">
            <div className="finding-header">
              <span className="badge sev-critical">CRITICAL</span>
              <span className="finding-title">Missing JWT_SECRET validation</span>
            </div>
            <div className="finding-desc">App will sign tokens with &quot;undefined&quot; as secret if env var is missing</div>
            <div className="finding-loc">src/utils/generateToken.js:14</div>
          </div>
          <div className="finding finding-high">
            <div className="finding-header">
              <span className="badge sev-high">HIGH</span>
              <span className="finding-title">No rate limiting on /api/auth/login</span>
            </div>
            <div className="finding-desc">Auth endpoints are not rate-limited, enabling brute force attacks</div>
            <div className="finding-loc">src/modules/auth/auth.routes.js:8</div>
          </div>
          <div className="finding finding-low">
            <div className="finding-header">
              <span className="badge sev-low">LOW</span>
              <span className="finding-title">CORS allows all origins in development</span>
            </div>
            <div className="finding-desc">Ensure CORS is restricted by environment in production builds</div>
            <div className="finding-loc">src/app.js:12</div>
          </div>
        </div>

        <div className="followup-card">
          <input className="input" type="text" placeholder="Ask a follow-up question about this analysis..." />
          <button className="btn btn-primary">Ask follow-up</button>
        </div>
        </div>
      </div>
    </div>
  )
}

export default ResultPage

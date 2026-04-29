import React from 'react'
import '../App.css'

const Analysis = () => {
  return (
    <div style={{ background: 'var(--bg-base)', minHeight: '580px' }}>
      <nav className="navbar">
        <div className="logo">Code<span className="logo-dot">.</span>Sage</div>
        <div className="nav-center"><span style={{ color: 'var(--text-tertiary)' }}>akshat / </span>codesage-backend</div>
        <div className="nav-right">
          <div className="avatar">AS</div>
          <button className="btn btn-ghost">Sign out</button>
        </div>
      </nav>

      <div style={{ padding: '16px 28px' }}>
        <div style={{ width: '100%', maxWidth: '1440px', margin: '0 auto' }}>
          <div className="analysis-layout">
        <div className="analysis-sidebar">
          <div className="sidebar-card">
            <div className="sidebar-section">
              <div className="sidebar-section-label">Repository</div>
              <div className="sidebar-row">
                <span className="sidebar-key">Name</span>
                <span className="sidebar-val">codesage-backend</span>
              </div>
              <div className="mt-4">
                <div className="sidebar-section-label">URL</div>
                <div style={{ fontSize: 11, color: 'var(--status-info)', fontFamily: 'var(--font-mono)', wordBreak: 'break-all', lineHeight: 1.5 }}>github.com/akshat/codesage-backend</div>
              </div>
              <div className="sidebar-row mt-8">
                <span className="sidebar-key">Branch</span>
                <span className="sidebar-val">main</span>
              </div>
            </div>
            <div className="divider mb-12"></div>
            <div className="sidebar-section">
              <div className="sidebar-section-label">Statistics</div>
              <div className="sidebar-row"><span className="sidebar-key">Files</span><span className="sidebar-val">142</span></div>
              <div className="sidebar-row mt-4"><span className="sidebar-key">Lines</span><span className="sidebar-val">8,430</span></div>
              <div className="sidebar-row mt-4"><span className="sidebar-key">Languages</span><span className="sidebar-val">4</span></div>
            </div>
            <div className="divider mb-12"></div>
            <div className="sidebar-section">
              <div className="sidebar-section-label">Composition</div>
              <div className="lang-bar-row">
                <div className="lang-bar-header"><span className="lang-bar-name">JavaScript</span><span className="lang-bar-pct">68%</span></div>
                <div className="lang-bar-track"><div className="lang-bar-fill" style={{ width: '68%', background: 'var(--status-warn)' }}></div></div>
              </div>
              <div className="lang-bar-row">
                <div className="lang-bar-header"><span className="lang-bar-name">Python</span><span className="lang-bar-pct">22%</span></div>
                <div className="lang-bar-track"><div className="lang-bar-fill" style={{ width: '22%', background: 'var(--status-info)' }}></div></div>
              </div>
              <div className="lang-bar-row">
                <div className="lang-bar-header"><span className="lang-bar-name">Other</span><span className="lang-bar-pct">10%</span></div>
                <div className="lang-bar-track"><div className="lang-bar-fill" style={{ width: '10%', background: 'var(--text-tertiary)' }}></div></div>
              </div>
            </div>
          </div>
        </div>

        <div className="analysis-main">
          <div className="query-card">
            <div className="query-title">Ask about this codebase</div>
            <textarea className="input" rows={3} style={{ resize: 'none', lineHeight: 1.65 }}>How is authentication implemented? Are there any security vulnerabilities in the JWT flow?</textarea>
            <div className="query-row">
              <select className="input" style={{ flex: 1, minWidth: 140 }}>
                <option>Security analysis</option>
                <option>Architecture overview</option>
                <option>Performance audit</option>
                <option>Code summary</option>
              </select>
              <button className="btn btn-primary">
                <svg width="10" height="10" viewBox="0 0 10 10" fill="none"><polygon points="1.5,1 9,5 1.5,9" fill="currentColor"/></svg>
                Analyze
              </button>
            </div>
          </div>

          <div className="query-card">
            <div className="output-header">
              <div className="output-title-row">
                <span className="output-title">Analysis output</span>
                <span className="badge badge-running"><span className="dot-pulse"></span>Streaming</span>
              </div>
              <span className="output-time">2.3s</span>
            </div>
            <div className="output-body">
              The authentication system uses JWT tokens with a dual-token strategy (access + refresh). Here's what I found:
              <br /><br />
              <span style={{ color: 'var(--status-warn)', fontWeight: 600 }}>Security concern:</span> The JWT secret is loaded from <span className="code-chip">process.env.JWT_SECRET</span> without validation — if this env var is missing, the app will sign tokens with <span className="code-chip" style={{ color: 'var(--syntax-str)' }}>&quot;undefined&quot;</span> as the key.
            </div>
            <div className="code-block mb-14">
              <div style={{ fontSize: 10, color: 'var(--text-tertiary)', marginBottom: 10, fontFamily: 'var(--font-sans)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <span>src/utils/generateToken.js</span>
                <span style={{ color: 'var(--status-success)' }}>cited</span>
              </div>
              <span className="code-kw">const</span> token = jwt.sign(<br />
              &nbsp;&nbsp;{`{ userId: user._id },`}<br />
              &nbsp;&nbsp;<span className="code-err">process.env.JWT_SECRET</span>, <span className="code-cmt">// ⚠ add fallback check</span><br />
              &nbsp;&nbsp;{`{ expiresIn: '15m' }`}<br />
              );<span className="typing-cursor"></span>
            </div>
            <div style={{ fontSize: 13, color: 'var(--text-secondary)' }}>
              Recommended fix: Add a startup check to throw if <span className="code-chip">JWT_SECRET</span> is unset...
            </div>
          </div>

          <div className="citations-card">
            <span className="section-label">Referenced files</span>
            <div className="file-ref">
              <svg width="12" height="12" viewBox="0 0 12 12" fill="none"><rect x="1" y="1" width="10" height="10" rx="2" stroke="var(--text-tertiary)" strokeWidth="1"/><path d="M3 4h6M3 6.5h4" stroke="var(--text-tertiary)" strokeWidth="1" strokeLinecap="round"/></svg>
              <span className="file-ref-name">src/utils/generateToken.js</span>
              <span className="file-ref-lines" style={{ color: 'var(--status-warn)' }}>L14–22</span>
            </div>
            <div className="file-ref">
              <svg width="12" height="12" viewBox="0 0 12 12" fill="none"><rect x="1" y="1" width="10" height="10" rx="2" stroke="var(--text-tertiary)" strokeWidth="1"/><path d="M3 4h6M3 6.5h4" stroke="var(--text-tertiary)" strokeWidth="1" strokeLinecap="round"/></svg>
              <span className="file-ref-name">src/middleware/auth.js</span>
              <span className="file-ref-lines">L5–30</span>
            </div>
          </div>

          <div className="citations-card">
            <div className="flex items-center justify-between mb-10">
              <span className="section-label">Analysis history</span>
              <svg width="10" height="6" viewBox="0 0 10 6" fill="none"><path d="M1 1l4 4 4-4" stroke="var(--text-tertiary)" strokeWidth="1.5" strokeLinecap="round"/></svg>
            </div>
            <div className="history-row">
              <span className="badge badge-done" style={{ fontSize: 9 }}>Done</span>
              <span className="history-label">Architecture overview</span>
              <span className="history-time">2h ago</span>
            </div>
            <div className="history-row">
              <span className="badge badge-fail" style={{ fontSize: 9 }}>Failed</span>
              <span className="history-label">Performance audit</span>
              <span className="history-time">1d ago</span>
            </div>
          </div>
        </div>
        </div>
      </div>
    </div>
    </div>
  )
}

export default Analysis

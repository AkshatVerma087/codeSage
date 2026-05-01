import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import '../App.css'

const Register = () => {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [emailError, setEmailError] = useState('')
  const [password, setPassword] = useState('')

  const checkEmailInUse = (value) => {
    // simulate server check: treat this address as already taken
    return value.trim().toLowerCase() === 'akshat@gmail.com'
  }

  const onEmailBlur = () => {
    if (!email) {
      setEmailError('')
      return
    }
    if (checkEmailInUse(email)) setEmailError('Email already in use')
    else setEmailError('')
  }

  return (
    <div className="auth-page grid-bg">
      <div className="auth-box">
        <div className="auth-logo">
          <div className="auth-logo-text">Code<span className="accent">Sage</span></div>
          <div className="auth-logo-sub">AI-powered code analysis</div>
        </div>

        <div className="auth-card">
          <div className="auth-title">Get started for free</div>

          <div className="field">
            <label className="field-label">Name</label>
            <input className="input" type="text" placeholder="Your name" value={name} onChange={(e) => setName(e.target.value)} />
          </div>

          <div className="field">
            <label className="field-label">Email address</label>
            <div className="input-icon-wrap">
              <svg className="input-icon" width="14" height="14" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg"><rect x="1" y="3" width="14" height="10" rx="2" stroke="currentColor" strokeWidth="1.2"/><path d="M1 5l7 5 7-5" stroke="currentColor" strokeWidth="1.2"/></svg>
              <input
                className={"input" + (emailError ? ' input-error' : '')}
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => { setEmail(e.target.value); setEmailError('') }}
                onBlur={onEmailBlur}
              />
            </div>
            {emailError ? <div className="error-text">{emailError}</div> : null}
          </div>

          <div className="field">
            <label className="field-label">Password</label>
            <div className="password-row">
              <input
                className="input"
                type="password"
                placeholder="••••••••••"
                value={password}
                onChange={(e) => { setPassword(e.target.value) }}
              />
            </div>
          </div>

          <div className="field">
            <label className="field-label">Confirm password</label>
            <div className="password-row">
              <input className="input" type="password" placeholder="••••••••••" />
            </div>
          </div>

          <div className="terms-row">
            <label className="checkbox">
              <input type="checkbox" defaultChecked />
              <span>I agree to the <a className="muted-link" href="#">Terms of Service</a> and <a className="muted-link" href="#">Privacy Policy</a></span>
            </label>
          </div>

          <button className="btn btn-primary w-full mt-4">Create account</button>

          <div className="auth-divider" style={{marginTop:16}}>
            <div className="auth-divider-line"></div>
            <span className="auth-divider-text">or continue with</span>
            <div className="auth-divider-line"></div>
          </div>

          <button className="github-btn">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg" style={{marginRight:8}}><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/></svg>
            GitHub
          </button>

          <div className="auth-footer-text">
            Already have an account? <Link to="/login" className="link">Sign in</Link>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Register

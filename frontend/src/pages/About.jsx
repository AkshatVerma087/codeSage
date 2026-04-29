import React from 'react'
import '../App.css'

const About = () => {
  return (
    <div style={{ background: 'var(--bg-base)', minHeight: '100vh' }}>
      <div style={{ padding: '16px 28px' }}>
        <div style={{ width: '100%', maxWidth: '1440px', margin: '0 auto' }}>
          {/* Header Section */}
          <div style={{ paddingTop: '40px', paddingBottom: '60px', textAlign: 'center' }}>
            <h1 style={{ fontSize: '48px', fontWeight: '800', letterSpacing: '-1.5px', color: 'var(--text-primary)', marginBottom: '16px' }}>
              About Code<span style={{ color: 'var(--accent)' }}>.</span>Sage
            </h1>
            <p style={{ fontSize: '18px', color: 'var(--text-secondary)', maxWidth: '600px', margin: '0 auto', lineHeight: '1.6' }}>
              Intelligent code analysis powered by AI. Uncover security issues, architectural insights, and code patterns in seconds.
            </p>
          </div>

          {/* Mission Section */}
          <div className="summary-card" style={{ marginBottom: '32px' }}>
            <div className="summary-card-title">Our Mission</div>
            <div className="summary-body">
              CodeSage empowers developers and security teams to understand their codebases faster. By combining advanced static analysis with AI-driven insights, we help teams identify vulnerabilities, optimize architecture, and maintain code quality at scale.
            </div>
          </div>

          {/* Features Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px', marginBottom: '48px' }}>
            <div style={{ padding: '20px', border: '1px solid var(--border-base)', borderRadius: '12px', background: 'var(--bg-raised)' }}>
              <div style={{ fontSize: '24px', marginBottom: '12px' }}>🔍</div>
              <div style={{ fontSize: '16px', fontWeight: '600', color: 'var(--text-primary)', marginBottom: '8px' }}>Deep Analysis</div>
              <p style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: '1.5', margin: 0 }}>
                Analyze entire repositories in seconds with comprehensive security, performance, and code quality checks.
              </p>
            </div>

            <div style={{ padding: '20px', border: '1px solid var(--border-base)', borderRadius: '12px', background: 'var(--bg-raised)' }}>
              <div style={{ fontSize: '24px', marginBottom: '12px' }}>🤖</div>
              <div style={{ fontSize: '16px', fontWeight: '600', color: 'var(--text-primary)', marginBottom: '8px' }}>AI-Powered Insights</div>
              <p style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: '1.5', margin: 0 }}>
                Get intelligent recommendations and explanations for code patterns, vulnerabilities, and improvements.
              </p>
            </div>

            <div style={{ padding: '20px', border: '1px solid var(--border-base)', borderRadius: '12px', background: 'var(--bg-raised)' }}>
              <div style={{ fontSize: '24px', marginBottom: '12px' }}>⚡</div>
              <div style={{ fontSize: '16px', fontWeight: '600', color: 'var(--text-primary)', marginBottom: '8px' }}>Lightning Fast</div>
              <p style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: '1.5', margin: 0 }}>
                Process large codebases quickly and get actionable results without slowing down your workflow.
              </p>
            </div>

            <div style={{ padding: '20px', border: '1px solid var(--border-base)', borderRadius: '12px', background: 'var(--bg-raised)' }}>
              <div style={{ fontSize: '24px', marginBottom: '12px' }}>🔐</div>
              <div style={{ fontSize: '16px', fontWeight: '600', color: 'var(--text-primary)', marginBottom: '8px' }}>Security First</div>
              <p style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: '1.5', margin: 0 }}>
                Identify vulnerabilities, CVEs, and security risks before they become problems.
              </p>
            </div>

            <div style={{ padding: '20px', border: '1px solid var(--border-base)', borderRadius: '12px', background: 'var(--bg-raised)' }}>
              <div style={{ fontSize: '24px', marginBottom: '12px' }}>📊</div>
              <div style={{ fontSize: '16px', fontWeight: '600', color: 'var(--text-primary)', marginBottom: '8px' }}>Detailed Reports</div>
              <p style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: '1.5', margin: 0 }}>
                Comprehensive analysis reports with code citations and actionable recommendations.
              </p>
            </div>

            <div style={{ padding: '20px', border: '1px solid var(--border-base)', borderRadius: '12px', background: 'var(--bg-raised)' }}>
              <div style={{ fontSize: '24px', marginBottom: '12px' }}>🎯</div>
              <div style={{ fontSize: '16px', fontWeight: '600', color: 'var(--text-primary)', marginBottom: '8px' }}>Multi-Language</div>
              <p style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: '1.5', margin: 0 }}>
                Support for JavaScript, Python, Go, Java, and more. Analyze any codebase.
              </p>
            </div>
          </div>

          {/* Technology Section */}
          <div className="summary-card" style={{ marginBottom: '32px' }}>
            <div className="summary-card-title">Built With Modern Tech</div>
            <div className="summary-body">
              CodeSage is built on a foundation of advanced AST (Abstract Syntax Tree) parsing, machine learning models, and pattern recognition algorithms. Our backend powers real-time analysis with distributed processing, while our frontend delivers an intuitive interface for exploring insights.
            </div>
          </div>

          {/* Contact Section */}
          <div style={{ padding: '32px', border: '1px solid var(--border-base)', borderRadius: '14px', background: 'var(--bg-raised)', textAlign: 'center', marginBottom: '60px' }}>
            <h3 style={{ fontSize: '20px', fontWeight: '700', color: 'var(--text-primary)', marginBottom: '12px' }}>Get in Touch</h3>
            <p style={{ fontSize: '14px', color: 'var(--text-secondary)', marginBottom: '20px' }}>Have questions or feedback? We'd love to hear from you.</p>
            <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
              <button className="btn btn-primary" style={{ cursor: 'pointer' }}>Contact Us</button>
              <button className="btn btn-secondary" style={{ cursor: 'pointer' }}>Documentation</button>
            </div>
          </div>

          {/* Footer Text */}
          <div style={{ textAlign: 'center', paddingBottom: '40px', borderTop: '1px solid var(--border-base)', paddingTop: '32px' }}>
            <p style={{ fontSize: '13px', color: 'var(--text-tertiary)', margin: 0 }}>
              © 2026 CodeSage. All rights reserved. | <span style={{ cursor: 'pointer' }}>Privacy Policy</span> · <span style={{ cursor: 'pointer' }}>Terms of Service</span>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default About

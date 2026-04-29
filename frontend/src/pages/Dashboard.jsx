import React, { useState, useEffect, useMemo, useContext } from 'react'
import { useNavigate } from 'react-router-dom'
import '../App.css'
import { AuthContext } from '../context/AuthContext'

const Dashboard = () => {
  const navigate = useNavigate()
  const { axiosInstance } = useContext(AuthContext)

  const [query, setQuery] = useState('')
  const SAMPLE_REPOS = [
    {
      _id: '1',
      name: 'codesage-backend',
      url: 'https://github.com/akshat/codesage-backend',
      provider: 'GitHub',
      defaultBranch: 'main',
      status: 'Completed',
      time: '2 hours ago',
      badgeClass: 'badge-done',
      actionClass: 'btn-sm-accent',
      actionLabel: 'Analyze',
      loading: false,
    },
    {
      _id: '2',
      name: 'ai-service-fastapi',
      url: 'https://github.com/akshat/ai-service-fastapi',
      provider: 'GitHub',
      defaultBranch: 'main',
      status: 'Running',
      time: 'just now',
      badgeClass: 'badge-running',
      actionClass: 'btn-sm-running',
      actionLabel: 'View',
      loading: false,
    },
    {
      _id: '3',
      name: 'react-frontend',
      url: 'https://github.com/akshat/react-frontend',
      provider: 'GitHub',
      defaultBranch: 'dev',
      status: 'Failed',
      time: 'Clone timeout',
      badgeClass: 'badge-fail',
      actionClass: 'btn-sm-danger',
      actionLabel: 'Retry',
      loading: false,
    },
  ]

  const [repoList, setRepoList] = useState(SAMPLE_REPOS)
  const [isPrivate, setIsPrivate] = useState(false)
  const [tokenValue, setTokenValue] = useState('')
  // controlled inputs for Add repository form
  const [newUrl, setNewUrl] = useState('')
  const [newBranch, setNewBranch] = useState('')
  const [newProvider, setNewProvider] = useState('GitHub')

  useEffect(() => {
    let mounted = true
    const load = async () => {
      try {
        const { data } = await axiosInstance.get('/api/repos')
        if (!mounted) return
        const mapped = (data.repos || []).map((r) => ({
          _id: r._id,
          name: (r.url || '').split('/').pop() || r.url,
          url: r.url,
          provider: r.provider,
          defaultBranch: r.defaultBranch,
          visibilityHint: r.visibilityHint,
          credentialRef: r.credentialRef,
          status: 'Completed',
          time: r.updatedAt || r.createdAt || 'just now',
          badgeClass: 'badge-done',
          actionClass: 'btn-sm-accent',
          actionLabel: 'Analyze',
          loading: false,
        }))
        setRepoList(mapped)
      } catch (err) {
        console.error('Failed to load repos', err)
      }
    }
    load()
    return () => { mounted = false }
  }, [axiosInstance])

  const filteredRepos = useMemo(() => {
    const q = query.trim().toLowerCase()
    if (!q) return repoList
    return repoList.filter((r) => [r.name, r.url, r.status].some((v) => String(v).toLowerCase().includes(q)))
  }, [query, repoList])

  function handleView(repo) {
    navigate(`/repo/${encodeURIComponent(repo._id || repo.name)}`)
  }

  function handleRerun(repo) {
    setRepoList((prev) => prev.map((r) => (r._id === repo._id ? { ...r, loading: true, status: 'Running' } : r)))
    axiosInstance.post(`/api/repos/${repo._id}/rerun`)
      .then(() => {
        setTimeout(() => {
          setRepoList((prev) => prev.map((r) => (r._id === repo._id ? { ...r, loading: false, status: 'Completed', time: 'just now', badgeClass: 'badge-done' } : r)))
        }, 800)
      })
      .catch((err) => {
        console.error('Rerun failed', err)
        alert('Failed to start run')
        setRepoList((prev) => prev.map((r) => (r._id === repo._id ? { ...r, loading: false, status: 'Failed', badgeClass: 'badge-fail' } : r)))
      })
  }

  function handleDelete(repo) {
    if (!window.confirm(`Delete repository ${repo.name}? This cannot be undone.`)) return
    setRepoList((prev) => prev.map((r) => (r._id === repo._id ? { ...r, loading: true } : r)))
    axiosInstance.delete(`/api/repos/${repo._id}`)
      .then(() => setRepoList((prev) => prev.filter((r) => r._id !== repo._id)))
      .catch((err) => {
        console.error('Delete failed', err)
        alert('Failed to delete repository')
        setRepoList((prev) => prev.map((r) => (r._id === repo._id ? { ...r, loading: false } : r)))
      })
  }

  function handleCancel() {
    setNewUrl('')
    setNewBranch('')
    setNewProvider('GitHub')
    setIsPrivate(false)
    setTokenValue('')
  }

  return (
    <div className='dashboard-page'>
      <div className="dashboard-box">
        <div className="dashboard-heading">
          <div>
            <h1 className="dashboard-title">Repositories</h1>
            <div className="dashboard-subtitle">{repoList.length} repos · last analyzed 2h ago</div>
          </div>
          <label className="dashboard-search" aria-label="Search repositories">
            <svg width="12" height="12" viewBox="0 0 12 12" fill="none" aria-hidden="true">
              <path d="M5.2 9.4a4.2 4.2 0 1 1 0-8.4 4.2 4.2 0 0 1 0 8.4Z" stroke="currentColor" strokeWidth="1.4" />
              <path d="M8.4 8.4 11 11" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" />
            </svg>
            <input type="search" placeholder="Search" value={query} onChange={(e) => setQuery(e.target.value)} />
          </label>
        </div>

        <div className="dashboard-stats">
          <div className="stat-card">
            <div className="stat-label">Total repos</div>
            <div className="stat-value">{repoList.length}</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Analyses run</div>
            <div className="stat-value">12</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Running now</div>
            <div className="stat-value stat-running">1</div>
          </div>
        </div>

        <div className="dashboard-content">
          <div className="repo-list">
            {filteredRepos.length > 0 ? filteredRepos.map((repo) => (
              <div className="repo-card" key={repo._id || repo.name}>
                <div className="repo-icon" aria-hidden="true">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="var(--text-tertiary)"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/></svg>
                </div>
                <div className="repo-info">
                  <div className="repo-name">{repo.name}</div>
                  <div className="repo-url">{repo.url}</div>
                </div>
                <div className="repo-status">
                  <span className={`badge ${repo.badgeClass}`}>
                    {repo.status === 'Running' ? <span className="dot-pulse" /> : null}
                    {repo.status}
                  </span>
                  <span className="repo-time">{repo.time}</span>
                </div>
                <div className="repo-actions">
                  <button className={`btn-sm ${repo.actionClass}`} type="button" onClick={() => handleRerun(repo)} disabled={repo.loading}>
                    {repo.loading ? <span className="btn-spinner" /> : repo.actionLabel}
                  </button>
                  <button className="btn-sm" type="button" onClick={() => handleView(repo)}>View</button>
                  <button className="btn-sm" type="button" onClick={() => handleDelete(repo)}>Delete</button>
                </div>
              </div>
            )) : (
              <div className="repo-empty">No repositories match your search.</div>
            )}
          </div>

          <div className="add-panel">
            <div className="add-panel-title">
              <svg width="12" height="12" viewBox="0 0 12 12" fill="none" aria-hidden="true">
                <path d="M6 1.5v9M1.5 6h9" stroke="var(--accent)" strokeWidth="2" strokeLinecap="round" />
              </svg>
              Add new repository
            </div>
            <div className="add-panel-grid">
              <div>
                <label className="field-label">Repository URL</label>
                <input className="input input-mono" type="text" placeholder="https://github.com/user/repo" value={newUrl} onChange={(e) => setNewUrl(e.target.value)} />
              </div>
              <div>
                <label className="field-label">Branch name</label>
                <input className="input input-mono" type="text" placeholder="main" value={newBranch} onChange={(e) => setNewBranch(e.target.value)} />
              </div>
              <div>
                <label className="field-label">Provider</label>
                <select className="input" value={newProvider} onChange={(e) => setNewProvider(e.target.value)}>
                  <option>GitHub</option>
                  <option>GitLab</option>
                  <option>Bitbucket</option>
                </select>
              </div>
            </div>

            <div className="toggle-row">
              <label style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <input type="checkbox" checked={isPrivate} onChange={(e) => setIsPrivate(e.target.checked)} />
                <span className="toggle-label">Private repository</span>
              </label>
              <span className="toggle-note">Requires GitHub token</span>
            </div>

            {isPrivate && (
              <div className="mb-16">
                <label className="field-label">GitHub access token</label>
                <input className="input input-mono" type="text" value={tokenValue} onChange={(e) => setTokenValue(e.target.value)} style={{ borderColor: 'var(--border-strong)' }} />
              </div>
            )}

            <div className="add-panel-actions">
              <button className="btn btn-primary" type="button">Add repository</button>
              <button className="btn btn-secondary" type="button" onClick={handleCancel}>Cancel</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard

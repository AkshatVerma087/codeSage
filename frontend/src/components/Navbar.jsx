import React, { useContext } from 'react'
import { AuthContext } from '../context/AuthContext'
import { useNavigate, useLocation } from 'react-router-dom'

const Navbar = () => {
  const { toggleTheme, isLight } = useContext(AuthContext)
  const navigate = useNavigate()
  const location = useLocation()

  const isActive = (path) => {
    return location.pathname === path ? 'pg-btn on' : 'pg-btn'
  }

  return (
    <nav className="demo-nav">
      <span className="demo-nav-label"></span>
      <button className={isActive('/dashboard')} onClick={() => navigate('/dashboard')}>Dashboard</button>
      <button className={isActive('/analysis')} onClick={() => navigate('/analysis')}>Analysis</button>
      <button className={isActive('/result')} onClick={() => navigate('/result')}>Result</button>
      <button className={isActive('/about')} onClick={() => navigate('/about')}>About</button>
      <div className="demo-spacer" />

      <div className="theme-toggle" onClick={toggleTheme} id="themeToggle" role="button" tabIndex={0}>
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" xmlns="http://www.w3.org/2000/svg" aria-hidden>
          <circle cx="12" cy="12" r="5"/>
          <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>
        </svg>
        {isLight ? 'Light mode' : 'Dark mode'}
      </div>
    </nav>
  )
}

export default Navbar

import React from 'react'
import { Navigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

const ProtectedRoute = ({ children }) => {
    const { user } = useAuth()
    const token = localStorage.getItem('token')

    // Dev-friendly bypass: set `localStorage.devMode = 'true'` to view
    // protected routes while developing the frontend without a backend.
    const isDev = (typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.DEV) || localStorage.getItem('devMode') === 'true'

    if (isDev) return children

    // Require either a persisted token OR a populated user in context
    if (!token && !user) {
        return <Navigate to="/login" replace />
    }

    return children
}

export default ProtectedRoute

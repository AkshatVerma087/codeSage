import React, { useState, createContext, useEffect } from 'react'
import axios from 'axios'

const AuthContext = createContext()

const axiosInstance = axios.create({
    baseURL: 'http://localhost:5000',
    withCredentials: true  // Send cookies with requests
})

const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null)
    const getInitialTheme = () => {
        try {
            const saved = localStorage.getItem('codesage:theme')
            if (saved === 'light') return true
            if (saved === 'dark') return false
        } catch (e) {
            // ignore
        }
        // fallback to prefers-color-scheme
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) return true
        return false
    }

    const [isLight, setIsLight] = useState(getInitialTheme)

    const toggleTheme = () => {
        setIsLight(prev => !prev)
    }

    useEffect(() => {
        try {
            localStorage.setItem('codesage:theme', isLight ? 'light' : 'dark')
        } catch (e) {
            // ignore
        }
        document.documentElement.classList.toggle('light', isLight)
    }, [isLight])

    return (
        <AuthContext.Provider value={{ user, setUser, axiosInstance, isLight, setIsLight, toggleTheme }}>
            {children}
        </AuthContext.Provider>
    )
}

export { AuthContext, AuthProvider }
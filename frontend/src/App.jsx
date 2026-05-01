import React from 'react'
import { RouterProvider } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import router from './app.routes'

const AppWithTheme = () => {
  return <RouterProvider router={router} />
}

const App = () => {
  return (
    <AuthProvider>
      <AppWithTheme />
    </AuthProvider>
  )
}

export default App

import { createBrowserRouter, Navigate } from "react-router-dom"
import Login from "./pages/Login"
import Register from "./pages/Register"
import Dashboard from "./pages/Dashboard"
import RepoPage from "./pages/RepoPage"
import ResultPage from "./pages/ResultPage"
import Analysis from "./pages/Analysis"
import About from "./pages/About"

import ProtectedRoute from "./components/ProtectedRoute"
import Layout from "./components/Layout"
const router = createBrowserRouter([
    {
        path: "/login",
        element: <Layout><Login /></Layout>
    },
    {
        path: "/register",
        element: <Layout><Register /></Layout>
    },
    {
        path: "/dashboard",
        element: <Layout><Dashboard /></Layout>
    },
    {
        path: "/analysis",
        element: <Layout><Analysis /></Layout>
    },
    {
        path: "/result",
        element: <Layout><ResultPage /></Layout>
    },
    {
        path: "/about",
        element: <Layout><About /></Layout>
    },
    {
        path: "/repo/:id",
        element: <Layout><RepoPage /></Layout>
    },
    {
        path: "/result/:id",
        element: <ProtectedRoute><Layout><ResultPage /></Layout></ProtectedRoute>
    },
    {
        path: "/",
        element: <Navigate to="/dashboard" replace />
    }
])

export default router
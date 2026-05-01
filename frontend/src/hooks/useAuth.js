import { useContext } from "react";
import { AuthContext } from "../context/AuthContext";
import * as authApi from '../api/auth.api'

export const useAuth = () => {
    const context = useContext(AuthContext)
    if (!context) throw new Error('useAuth must be inside AuthProvider')

    const { user, setUser, token, setToken, loading, setLoading, error, setError, axiosInstance } = context;

    const login = async ({ email, password }) => {
        try {
            setLoading(true);
            setError(null);
            const data = await authApi.login({ email, password }, axiosInstance);
            setUser(data.user);
            setToken(data.accessToken);
            localStorage.setItem('authToken', data.accessToken);
            return data;
        } catch (err) {
            const message = err.response?.data?.message || 'Login failed';
            setError(message);
            throw err;
        } finally {
            setLoading(false);
        }
    }

    const register = async ({ name, email, password }) => {
        try {
            setLoading(true);
            setError(null);
            const data = await authApi.register({ name, email, password }, axiosInstance);
            setUser(data.user);
            setToken(data.accessToken);
            localStorage.setItem('authToken', data.accessToken);
            return data;
        } catch (err) {
            const message = err.response?.data?.message || 'Registration failed';
            setError(message);
            throw err;
        } finally {
            setLoading(false);
        }
    }

    const logout = async () => {
        try {
            setLoading(true);
            await authApi.logout(axiosInstance);
        } catch (err) {
            console.error('Logout error:', err);
        } finally {
            setUser(null);
            setToken(null);
            localStorage.removeItem('authToken');
            setLoading(false);
        }
    }

    return { user, setUser, token, loading, error, setError, login, register, logout };
}
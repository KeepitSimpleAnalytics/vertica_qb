import React, { createContext, useState, useContext } from 'react';
import axios from 'axios';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [token, setToken] = useState(localStorage.getItem('authToken'));
    const [user, setUser] = useState(localStorage.getItem('authUser'));
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    // Use the same hostname as frontend but port 8000
    const getBackendUrl = () => {
        const hostname = window.location.hostname;
        return `http://${hostname}:8000`;
    };

    const login = async (username, password) => {
        setLoading(true);
        setError('');
        
        try {
            const params = new URLSearchParams();
            params.append('username', username);
            params.append('password', password);

            const backendUrl = getBackendUrl();
            console.log('Backend URL:', backendUrl); // Debug log
            
            const response = await axios.post(`${backendUrl}/token`, params, {
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                timeout: 10000 // 10 second timeout
            });

            const { access_token } = response.data;
            setToken(access_token);
            setUser(username);
            localStorage.setItem('authToken', access_token);
            localStorage.setItem('authUser', username);
            setError('');
            return true;
            
        } catch (err) {
            console.error('Login error:', err);
            
            if (err.code === 'ECONNREFUSED') {
                setError('Cannot connect to server. Please ensure the backend is running.');
            } else if (err.response) {
                // Server responded with error
                const status = err.response.status;
                const detail = err.response.data?.detail || 'Unknown error';
                
                if (status === 401) {
                    setError('Invalid username or password.');
                } else if (status === 503) {
                    setError('Database server is unavailable. Please try again later.');
                } else if (status === 500) {
                    setError('Server configuration error. Please contact administrator.');
                } else {
                    setError(`Login failed: ${detail}`);
                }
            } else if (err.request) {
                setError('No response from server. Please check your network connection.');
            } else {
                setError('An unexpected error occurred. Please try again.');
            }
            return false;
        } finally {
            setLoading(false);
        }
    };

    const logout = () => {
        setToken(null);
        setUser(null);
        localStorage.removeItem('authToken');
        localStorage.removeItem('authUser');
        setError('');
    };

    return (
        <AuthContext.Provider value={{ token, user, login, logout, error, loading }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    return useContext(AuthContext);
};
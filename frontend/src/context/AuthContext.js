import React, { createContext, useState, useContext } from 'react';
import axios from 'axios';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [token, setToken] = useState(localStorage.getItem('authToken'));
    const [user, setUser] = useState(localStorage.getItem('authUser'));
    const [error, setError] = useState('');

    const login = async (username, password) => {
        try {
            const params = new URLSearchParams();
            params.append('username', username);
            params.append('password', password);

            const response = await axios.post('http://localhost:8000/token', params, {
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
            });

            const { access_token } = response.data;
            setToken(access_token);
            setUser(username);
            localStorage.setItem('authToken', access_token);
            localStorage.setItem('authUser', username);
            setError('');
            return true;
        } catch (err) {
            setError('Login failed. Please check your credentials.');
            return false;
        }
    };

    const logout = () => {
        setToken(null);
        setUser(null);
        localStorage.removeItem('authToken');
        localStorage.removeItem('authUser');
    };

    return (
        <AuthContext.Provider value={{ token, user, login, logout, error }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    return useContext(AuthContext);
};

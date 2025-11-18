import { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../services/api';

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is logged in
    const token = localStorage.getItem('token');
    const savedUser = localStorage.getItem('user');

    if (token && savedUser) {
      setUser(JSON.parse(savedUser));
    }
    setLoading(false);
  }, []);

  const login = async (username, password) => {
    try {
      // Simulate login without backend validation
      const mockUsers = {
        'admin': { id: 1, username: 'admin', email: 'admin@perfo.ai', full_name: 'Admin User', role: 'admin', is_active: true },
        'finance_manager': { id: 2, username: 'finance_manager', email: 'finance@perfo.ai', full_name: 'Finance Manager', role: 'finance_manager', is_active: true },
        'approver': { id: 3, username: 'approver', email: 'approver@perfo.ai', full_name: 'Invoice Approver', role: 'approver', is_active: true },
        'viewer': { id: 4, username: 'viewer', email: 'viewer@perfo.ai', full_name: 'Read Only User', role: 'viewer', is_active: true }
      };

      const userData = mockUsers[username];

      if (!userData) {
        return {
          success: false,
          error: 'Invalid username',
        };
      }

      // Save mock token and user data
      localStorage.setItem('token', 'mock-token-' + username);
      localStorage.setItem('user', JSON.stringify(userData));
      setUser(userData);

      return { success: true };
    } catch (error) {
      console.error('Login error:', error);
      return {
        success: false,
        error: 'Login failed',
      };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
  };

  const value = {
    user,
    login,
    logout,
    isAuthenticated: !!user,
    loading,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

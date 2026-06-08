// AuthContext.jsx — global login state for the whole app
// React Context lets ANY component know "is the user logged in?"
// without passing props through every level of the component tree.

import { createContext, useContext, useState, useEffect } from 'react';
import { login as loginApi } from '../api/authApi';

// Step 1: Create the context (empty box that will hold auth data)
const AuthContext = createContext(null);

// Step 2: Provider — wraps the whole app and PROVIDES the auth data
export function AuthProvider({ children }) {
  // State: current logged-in user object (null if not logged in)
  const [user, setUser] = useState(null);
  // State: JWT token string
  const [token, setToken] = useState(null);
  // State: true while we're checking localStorage on first load
  const [loading, setLoading] = useState(true);

  // On app startup, check if there's a saved token in localStorage
  // This keeps you logged in after a page refresh
  useEffect(() => {
    const savedToken = localStorage.getItem('token');
    const savedUser = localStorage.getItem('user');
    if (savedToken && savedUser) {
      setToken(savedToken);
      setUser(JSON.parse(savedUser));
    }
    setLoading(false);
  }, []);

  // login() — called from LoginPage when user submits the form
  const login = async (email, password) => {
    const data = await loginApi(email, password);
    // Save token and user to both state AND localStorage
    setToken(data.access_token);
    setUser(data.user);
    localStorage.setItem('token', data.access_token);
    localStorage.setItem('user', JSON.stringify(data.user));
    return data;
  };

  // logout() — clears everything and sends user to login page
  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  };

  // isAuthenticated — true if we have both a user and a token
  const isAuthenticated = !!token && !!user;

  // Provide all this data to any component that calls useAuth()
  return (
    <AuthContext.Provider value={{ user, token, login, logout, isAuthenticated, loading }}>
      {children}
    </AuthContext.Provider>
  );
}

// Step 3: Custom hook — makes it easy to USE the context in any component
// Usage: const { user, login, logout } = useAuth();
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used inside AuthProvider');
  return context;
}

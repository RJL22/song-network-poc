// AuthContext.tsx
import { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import { setUnauthorized, apiFetch } from '../api/client';

interface AuthContextType {
  token: string | null;
  user: User | null;
  isAuthenticated: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
}

export interface User { id: number; username: string }

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    apiFetch<User>("/auth/me").then((current) => {
      setToken("cookie");
      setUser(current);
    }).catch(() => setToken(null));
  }, []);

  const [user, setUser] = useState<User | null>(null);

  async function login(username: string, password: string) {
    // TODO: POST /auth/login via your client.ts
    // TODO: on success — setToken(...) and localStorage.setItem(...)
    // TODO: on failure — throw so the login form can show an error
    await apiFetch<User>("/auth/login", {
        method: "POST",
        body: JSON.stringify({ username, password }),
    });
    const current = await apiFetch<User>("/auth/me");
    setToken("cookie");
    setUser(current);
  }

  function logout() {
    void apiFetch<void>("/auth/logout", { method: "POST" });
    setToken(null);
    setUser(null);
  }

  useEffect(() => {
    setUnauthorized(logout);
  }, []);

  const value: AuthContextType = {
    token,
    user,
    isAuthenticated: !!token,
    login,
    logout,
  };


  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}

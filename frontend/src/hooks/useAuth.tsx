import { useQuery, useQueryClient } from "@tanstack/react-query";
import axios from "axios";
import { createContext, ReactNode, useContext, useState } from "react";
import { API_BASE_URL, api, clearToken, getToken, setToken } from "@/lib/api";
import type { Farmer } from "@/types/api";

interface AuthContextValue {
  farmer: Farmer | null | undefined;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string, phone?: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const queryClient = useQueryClient();
  const [hasToken, setHasToken] = useState(!!getToken());

  const { data: farmer, isLoading } = useQuery({
    queryKey: ["me"],
    queryFn: async () => (await api.get<Farmer>("/auth/me")).data,
    enabled: hasToken,
    retry: false,
  });

  async function login(email: string, password: string) {
    const form = new URLSearchParams();
    form.set("username", email);
    form.set("password", password);
    const res = await axios.post(`${API_BASE_URL}/api/v1/auth/login`, form, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });
    setToken(res.data.access_token);
    setHasToken(true);
    await queryClient.invalidateQueries({ queryKey: ["me"] });
  }

  async function register(name: string, email: string, password: string, phone?: string) {
    const res = await axios.post(`${API_BASE_URL}/api/v1/auth/register`, {
      name,
      email,
      password,
      phone,
    });
    setToken(res.data.access_token);
    setHasToken(true);
    await queryClient.invalidateQueries({ queryKey: ["me"] });
  }

  function logout() {
    clearToken();
    setHasToken(false);
    queryClient.clear();
  }

  return (
    <AuthContext.Provider
      value={{
        farmer,
        isLoading: hasToken && isLoading,
        isAuthenticated: hasToken && !!farmer,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}

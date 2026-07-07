import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export type Role = 'employee' | 'manager' | 'hr' | 'super_admin'
export interface User {
  id: number; emp_code: string; email: string
  first_name: string; last_name: string; role: Role
}

interface AuthState {
  access: string | null
  refresh: string | null
  user: User | null
  setTokens: (a: string, r: string) => void
  setUser: (u: User) => void
  logout: () => void
}

export const useAuth = create<AuthState>()(
  persist(
    (set) => ({
      access: null,
      refresh: null,
      user: null,
      setTokens: (access, refresh) => set({ access, refresh }),
      setUser: (user) => set({ user }),
      logout: () => set({ access: null, refresh: null, user: null }),
    }),
    { name: 'eams-auth' },
  ),
)

export const atLeast = (role: Role | undefined, min: Role) => {
  const order: Role[] = ['employee', 'manager', 'hr', 'super_admin']
  return role ? order.indexOf(role) >= order.indexOf(min) : false
}

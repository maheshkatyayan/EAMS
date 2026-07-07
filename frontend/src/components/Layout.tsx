import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useAuth, atLeast } from '../store/auth'
import { api } from '../lib/api'

const links = [
  { to: '/', label: 'Dashboard', min: 'employee' },
  { to: '/attendance', label: 'Attendance', min: 'employee' },
  { to: '/leaves', label: 'Leaves', min: 'employee' },
  { to: '/employees', label: 'Employees', min: 'manager' },
  { to: '/reports', label: 'Reports', min: 'manager' },
  { to: '/audit', label: 'Audit log', min: 'super_admin' },
] as const

export default function Layout() {
  const { user, refresh, logout } = useAuth()
  const nav = useNavigate()
  const out = async () => {
    if (refresh) await api.post('/auth/logout', { refresh_token: refresh }).catch(() => {})
    logout(); nav('/login')
  }
  return (
    <div className="flex min-h-screen">
      <aside className="w-56 shrink-0 bg-ink text-slate-300 flex flex-col">
        <div className="px-5 py-6 font-display text-xl font-bold text-white tracking-tight">
          EAMS<span className="text-amber-punch">.</span>
        </div>
        <nav className="flex-1 px-2 space-y-1">
          {links.filter((l) => atLeast(user?.role, l.min)).map((l) => (
            <NavLink key={l.to} to={l.to} end={l.to === '/'}
              className={({ isActive }) =>
                `block rounded-lg px-3 py-2 text-sm ${isActive ? 'bg-inkline text-white font-medium' : 'hover:bg-inkline/60'}`}>
              {l.label}
            </NavLink>
          ))}
        </nav>
        <div className="px-5 py-4 border-t border-inkline text-xs">
          <div className="text-white font-medium">{user?.first_name} {user?.last_name}</div>
          <div className="capitalize text-slate-400">{user?.role.replace('_', ' ')}</div>
          <button onClick={out} className="mt-2 text-amber-punch hover:underline">Sign out</button>
        </div>
      </aside>
      <main className="flex-1 p-6 lg:p-8 max-w-6xl">
        <Outlet />
      </main>
    </div>
  )
}

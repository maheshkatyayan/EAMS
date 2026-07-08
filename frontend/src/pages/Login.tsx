import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../lib/api'
import { useAuth } from '../store/auth'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [err, setErr] = useState('')
  const [busy, setBusy] = useState(false)
  const { setTokens, setUser } = useAuth()
  const nav = useNavigate()

  const submit = async () => {
    setBusy(true); setErr('')
    try {
      const r = await api.post('/auth/login', { email, password })
      setTokens(r.data.access_token, r.data.refresh_token)
      const me = await api.get('/employees/me')
      setUser(me.data)
      nav('/')
    } catch (e: any) {
      setErr(e.response?.data?.detail ?? 'Sign in failed')
    } finally { setBusy(false) }
  }

  return (
    <div className="min-h-screen grid place-items-center bg-ink">
      <div className="w-full max-w-sm card">
        <h1 className="font-display text-2xl font-bold mb-1">EAMS<span className="text-amber-punch">.</span></h1>
        <p className="text-sm text-slate-500 mb-6">Sign in to record your day.</p>
        <label className="block text-sm font-medium mb-1">Email</label>
        <input className="input mb-4" value={email} onChange={(e) => setEmail(e.target.value)}
               onKeyDown={(e) => e.key === 'Enter' && submit()} placeholder="you@company.com" />
        <label className="block text-sm font-medium mb-1">Password</label>
        <input className="input mb-4" type="password" value={password}
               onChange={(e) => setPassword(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && submit()} />
        {err && <p className="text-sm text-red-600 mb-3">{err}</p>}
        <button className="btn-primary w-full" onClick={submit} disabled={busy || !email || !password}>
          {busy ? 'Signing in…' : 'Sign in'}
        </button>

        {/* <button type="button" className="w-full mt-3 text-sm text-slate-700 hover:text-slate-900" onClick={() => nav('/register')}>
          Register a new account
        </button> */}
      </div>
    </div>
  )
}

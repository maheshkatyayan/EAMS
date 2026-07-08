import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../lib/api'
import { useAuth } from '../store/auth'

export default function Register() {
  const [empCode, setEmpCode] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [firstName, setFirstName] = useState('')
  const [lastName, setLastName] = useState('')
  const [phone, setPhone] = useState('')
  const [designation, setDesignation] = useState('')
  const [dateJoined, setDateJoined] = useState('')
  const [err, setErr] = useState('')
  const [busy, setBusy] = useState(false)
  const { setTokens, setUser } = useAuth()
  const nav = useNavigate()

  const submit = async () => {
    setBusy(true)
    setErr('')
    try {
      const r = await api.post('/auth/register', {
        emp_code: empCode,
        email,
        password,
        first_name: firstName,
        last_name: lastName,
        phone: phone || undefined,
        designation: designation || undefined,
        date_joined: dateJoined || undefined,
      })
      setTokens(r.data.access_token, r.data.refresh_token)
      const me = await api.get('/employees/me')
      setUser(me.data)
      nav('/')
    } catch (e: any) {
      setErr(e.response?.data?.detail ?? 'Registration failed')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="min-h-screen grid place-items-center bg-ink">
      <div className="w-full max-w-lg card">
        <h1 className="font-display text-2xl font-bold mb-1">Register<span className="text-amber-punch">.</span></h1>
        <p className="text-sm text-slate-500 mb-6">Create your employee account.</p>

        <label className="block text-sm font-medium mb-1">Employee Code</label>
        <input className="input mb-4" value={empCode} onChange={(e) => setEmpCode(e.target.value)} placeholder="EMP006" />

        <label className="block text-sm font-medium mb-1">Email</label>
        <input className="input mb-4" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@company.com" />

        <label className="block text-sm font-medium mb-1">Password</label>
        <input className="input mb-4" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />

        <div className="grid gap-4 md:grid-cols-2">
          <div>
            <label className="block text-sm font-medium mb-1">First Name</label>
            <input className="input mb-4" value={firstName} onChange={(e) => setFirstName(e.target.value)} />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Last Name</label>
            <input className="input mb-4" value={lastName} onChange={(e) => setLastName(e.target.value)} />
          </div>
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          <div>
            <label className="block text-sm font-medium mb-1">Phone</label>
            <input className="input mb-4" value={phone} onChange={(e) => setPhone(e.target.value)} placeholder="1234567890" />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Designation</label>
            <input className="input mb-4" value={designation} onChange={(e) => setDesignation(e.target.value)} placeholder="hr" />
          </div>
        </div>

        <label className="block text-sm font-medium mb-1">Date Joined</label>
        <input className="input mb-4" type="date" value={dateJoined} onChange={(e) => setDateJoined(e.target.value)} />

        {err && <p className="text-sm text-red-600 mb-3">{err}</p>}

        <button className="btn-primary w-full" onClick={submit} disabled={busy || !empCode || !email || !password || !firstName}>
          {busy ? 'Registering…' : 'Register'}
        </button>

        <button type="button" className="w-full mt-3 text-sm text-slate-700 hover:text-slate-900" onClick={() => nav('/login')}>
          Already have an account? Sign in
        </button>
      </div>
    </div>
  )
}

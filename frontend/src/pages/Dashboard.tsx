import { useEffect, useState } from 'react'
import { api } from '../lib/api'
import { useAuth, atLeast } from '../store/auth'
import { useLiveEvents } from '../lib/ws'

interface Today {
  check_in: string | null; check_out: string | null
  working_hours: number; is_late: boolean; status: string
}

export default function Dashboard() {
  const { user } = useAuth()
  const [now, setNow] = useState(new Date())
  const [today, setToday] = useState<Today | null>(null)
  const [stats, setStats] = useState<any>(null)
  const [feed, setFeed] = useState<string[]>([])
  const [err, setErr] = useState('')

  useEffect(() => { const t = setInterval(() => setNow(new Date()), 1000); return () => clearInterval(t) }, [])

  const load = async () => {
    const d = new Date().toISOString().slice(0, 10)
    const r = await api.get(`/attendance/me?start=${d}&end=${d}`)
    setToday(r.data[0] ?? null)
    if (atLeast(user?.role, 'manager')) {
      setStats((await api.get('/reports/dashboard')).data)
    }
  }
  useEffect(() => { load() }, [])

  useLiveEvents((e) => {
    if (e.event === 'check_in') setFeed((f) => [`${e.name} checked in${e.late ? ' (late)' : ''}`, ...f].slice(0, 8))
    if (e.event === 'check_out') setFeed((f) => [`${e.name} checked out — ${e.hours}h`, ...f].slice(0, 8))
    if (e.event === 'leave_request') setFeed((f) => [`${e.name} requested leave`, ...f].slice(0, 8))
  })

  const punch = async (kind: 'check-in' | 'check-out') => {
    setErr('')
    const pos = await new Promise<GeolocationPosition | null>((res) =>
      navigator.geolocation
        ? navigator.geolocation.getCurrentPosition(res, () => res(null), { timeout: 3000 })
        : res(null))
    try {
      await api.post(`/attendance/${kind}`, {
        latitude: pos?.coords.latitude ?? null,
        longitude: pos?.coords.longitude ?? null,
        device_info: navigator.userAgent.slice(0, 200),
      })
      load()
    } catch (e: any) { setErr(e.response?.data?.detail ?? 'Failed') }
  }

  const time = (s: string | null) => (s ? new Date(s).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '—')

  return (
    <div className="space-y-6">
      <h1 className="font-display text-2xl font-bold">Good day, {user?.first_name}</h1>

      <div className="card bg-ink text-white border-none">
        <div className="flex flex-wrap items-center justify-between gap-6">
          <div>
            <div className="font-mono text-4xl tracking-tight">{now.toLocaleTimeString()}</div>
            <div className="text-slate-400 text-sm mt-1">
              {now.toLocaleDateString(undefined, { weekday: 'long', day: 'numeric', month: 'long' })}
            </div>
          </div>
          <div className="flex items-center gap-6">
            <div className="text-sm text-slate-300">
              <div>In: <span className="font-mono">{time(today?.check_in ?? null)}</span></div>
              <div>Out: <span className="font-mono">{time(today?.check_out ?? null)}</span></div>
              {today?.is_late && <span className="badge bg-amber-punch/20 text-amber-punch mt-1">Late arrival</span>}
            </div>
            {!today?.check_in ? (
              <button className="btn bg-amber-punch text-ink hover:brightness-110 text-base px-6 py-3" onClick={() => punch('check-in')}>
                Check in
              </button>
            ) : !today?.check_out ? (
              <button className="btn bg-white text-ink hover:bg-slate-200 text-base px-6 py-3" onClick={() => punch('check-out')}>
                Check out
              </button>
            ) : (
              <div className="text-right">
                <div className="font-mono text-2xl">{today.working_hours}h</div>
                <div className="text-xs text-slate-400">day complete</div>
              </div>
            )}
          </div>
        </div>
        {err && <p className="text-sm text-red-400 mt-3">{err}</p>}
      </div>

      {stats && (
        <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
          {[
            ['Employees', stats.total_employees],
            ['Checked in', stats.checked_in],
            ['Late today', stats.late],
            ['On leave', stats.on_leave],
            ['Pending leaves', stats.pending_leaves],
          ].map(([k, v]) => (
            <div key={k as string} className="card">
              <div className="text-2xl font-display font-bold">{v as number}</div>
              <div className="text-xs text-slate-500">{k}</div>
            </div>
          ))}
        </div>
      )}

      {feed.length > 0 && (
        <div className="card">
          <h2 className="font-semibold mb-2 text-sm">Live activity</h2>
          <ul className="space-y-1 text-sm text-slate-600">
            {feed.map((f, i) => <li key={i}>• {f}</li>)}
          </ul>
        </div>
      )}
    </div>
  )
}

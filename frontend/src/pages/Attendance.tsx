import { useEffect, useState } from 'react'
import { api } from '../lib/api'

const badge: Record<string, string> = {
  present: 'bg-teal/10 text-teal', half_day: 'bg-amber-punch/10 text-amber-punch',
  on_leave: 'bg-blue-100 text-blue-700', absent: 'bg-red-100 text-red-700',
  holiday: 'bg-slate-100 text-slate-600',
}

export default function Attendance() {
  const [rows, setRows] = useState<any[]>([])
  useEffect(() => { api.get('/attendance/me').then((r) => setRows(r.data)) }, [])
  const t = (s: string | null) => (s ? new Date(s).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '—')
  return (
    <div className="space-y-4">
      <h1 className="font-display text-2xl font-bold">My attendance</h1>
      <div className="card overflow-x-auto p-0">
        <table className="w-full">
          <thead><tr>
            <th className="th">Date</th><th className="th">In</th><th className="th">Out</th>
            <th className="th">Hours</th><th className="th">OT</th><th className="th">Status</th><th className="th">Flags</th>
          </tr></thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.id}>
                <td className="td font-mono">{r.date}</td>
                <td className="td font-mono">{t(r.check_in)}</td>
                <td className="td font-mono">{t(r.check_out)}</td>
                <td className="td">{r.working_hours}</td>
                <td className="td">{r.overtime_hours > 0 ? `+${r.overtime_hours}` : '—'}</td>
                <td className="td"><span className={`badge ${badge[r.status] ?? ''}`}>{r.status.replace('_', ' ')}</span></td>
                <td className="td text-xs text-slate-500">
                  {r.is_late && 'late '}{r.early_exit && 'early exit'}
                </td>
              </tr>
            ))}
            {rows.length === 0 && <tr><td className="td text-slate-500" colSpan={7}>No records yet — check in from the dashboard.</td></tr>}
          </tbody>
        </table>
      </div>
    </div>
  )
}

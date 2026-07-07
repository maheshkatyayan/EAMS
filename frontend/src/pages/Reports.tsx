import { useState } from 'react'
import { api } from '../lib/api'
import { useAuth, atLeast } from '../store/auth'

export default function Reports() {
  const { user } = useAuth()
  const now = new Date()
  const [year, setYear] = useState(now.getFullYear())
  const [month, setMonth] = useState(now.getMonth() + 1)
  const [empId, setEmpId] = useState(user?.id ?? 0)
  const [data, setData] = useState<any>(null)

  const run = async () => setData((await api.get(`/reports/monthly/${empId}?year=${year}&month=${month}`)).data)
  const download = () => window.open(`/api/v1/reports/export?year=${year}&month=${month}`, '_blank')

  return (
    <div className="space-y-4">
      <h1 className="font-display text-2xl font-bold">Reports</h1>
      <div className="card flex flex-wrap items-end gap-3">
        <div><label className="text-xs text-slate-500">Employee ID</label>
          <input className="input w-28" type="number" value={empId} onChange={(e) => setEmpId(+e.target.value)} /></div>
        <div><label className="text-xs text-slate-500">Year</label>
          <input className="input w-24" type="number" value={year} onChange={(e) => setYear(+e.target.value)} /></div>
        <div><label className="text-xs text-slate-500">Month</label>
          <input className="input w-20" type="number" min={1} max={12} value={month} onChange={(e) => setMonth(+e.target.value)} /></div>
        <button className="btn-primary" onClick={run}>Run</button>
        {atLeast(user?.role, 'hr') && <button className="btn-ghost" onClick={download}>Export org CSV</button>}
      </div>
      {data && (
        <div className="grid grid-cols-2 lg:grid-cols-6 gap-4">
          {[['Present', data.present_days], ['Half days', data.half_days], ['Leave', data.leave_days],
            ['Late', data.late_days], ['Hours', data.total_hours], ['Overtime', data.overtime_hours]].map(([k, v]) => (
            <div key={k as string} className="card">
              <div className="text-2xl font-display font-bold">{v as number}</div>
              <div className="text-xs text-slate-500">{k}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

import { useEffect, useState } from 'react'
import { api } from '../lib/api'

export default function Audit() {
  const [rows, setRows] = useState<any[]>([])
  const [action, setAction] = useState('')
  useEffect(() => {
    api.get('/audit', { params: action ? { action } : {} }).then((r) => setRows(r.data))
  }, [action])
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="font-display text-2xl font-bold">Audit log</h1>
        <input className="input w-56" placeholder="Filter by action…" value={action} onChange={(e) => setAction(e.target.value)} />
      </div>
      <div className="card p-0 overflow-x-auto">
        <table className="w-full">
          <thead><tr><th className="th">When</th><th className="th">Actor</th><th className="th">Action</th><th className="th">Entity</th><th className="th">IP</th></tr></thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.id}>
                <td className="td font-mono text-xs">{new Date(r.created_at).toLocaleString()}</td>
                <td className="td">#{r.actor_id ?? '—'}</td>
                <td className="td font-mono text-xs">{r.action}</td>
                <td className="td text-xs">{r.entity}{r.entity_id ? ` #${r.entity_id}` : ''}</td>
                <td className="td font-mono text-xs">{r.ip_address ?? '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

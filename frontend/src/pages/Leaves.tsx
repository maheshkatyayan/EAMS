import { useEffect, useState } from 'react'
import { api } from '../lib/api'
import { useAuth, atLeast } from '../store/auth'

export default function Leaves() {
const { user } = useAuth()
const isMgr = atLeast(user?.role, 'manager')

const [types, setTypes] = useState<any[]>([])
const [balance, setBalance] = useState<any[]>([])
const [mine, setMine] = useState<any[]>([])
const [pending, setPending] = useState<any[]>([])

const [form, setForm] = useState({
leave_type_id: null as number | null,
start_date: '',
end_date: '',
reason: ''
})

const [msg, setMsg] = useState('')

const load = async () => {
try {
const [t, b, m] = await Promise.all([
api.get('/leaves/types'),
api.get('/leaves/balance'),
api.get('/leaves/mine')
])
console.log('Leave types:', t.data)
console.log('Leave balance:', b.data)
console.log('My leaves:', m.data) 

  setTypes(t.data)
  setBalance(b.data)
  setMine(m.data)

  // Set default leave type if not selected
  if (t.data.length > 0) {
    setForm((f) => ({
      ...f,
      leave_type_id: f.leave_type_id || t.data[0].id
    }))
  }

  if (isMgr) {
    const p = await api.get('/leaves/pending')
    setPending(p.data)
  }
} catch (err) {
  console.error(err)
}


}

useEffect(() => {
load()
}, [])

const apply = async () => {
setMsg('')

if (!form.leave_type_id) {
  setMsg('Please select leave type')
  return
}

if (!form.start_date || !form.end_date) {
  setMsg('Please select dates')
  return
}

try {
  await api.post('/leaves', form)
  setMsg('Request submitted.')
  load()
} catch (e: any) {
  setMsg(e.response?.data?.detail ?? 'Failed')
}


}

const review = async (id: number, approve: boolean) => {
await api.post(`/leaves/${id}/review`, { approve })
load()
}

const cancelLeave = async (id: number) => {
await api.post(`/leaves/${id}/cancel`)
load()
}

return ( <div className="space-y-6"> <h1 className="font-display text-2xl font-bold">Leaves</h1>


  {/* Balance */}
  <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
    {balance.map((b) => (
      <div key={b.leave_type_id} className="card">
        <div className="text-2xl font-display font-bold">
          {b.remaining}
          <span className="text-sm text-slate-400">/{b.quota}</span>
        </div>
        <div className="text-xs text-slate-500">
          {b.name} remaining
        </div>
      </div>
    ))}
  </div>

  {/* Apply Leave */}
  <div className="card space-y-3">
    <h2 className="font-semibold">Apply for leave</h2>

    <div className="grid sm:grid-cols-4 gap-3">
      <select
        className="input"
        value={form.leave_type_id ?? ''}
        onChange={(e) =>
          setForm({ ...form, leave_type_id: Number(e.target.value) })
        }
      >
        {types.map((t) => (
          <option key={t.id} value={t.id}>
            {t.name}
          </option>
        ))}
      </select>

      <input
        className="input"
        type="date"
        value={form.start_date}
        onChange={(e) =>
          setForm({ ...form, start_date: e.target.value })
        }
      />

      <input
        className="input"
        type="date"
        value={form.end_date}
        onChange={(e) =>
          setForm({ ...form, end_date: e.target.value })
        }
      />

      <input
        className="input"
        placeholder="Reason"
        value={form.reason}
        onChange={(e) =>
          setForm({ ...form, reason: e.target.value })
        }
      />
    </div>

    <div className="flex items-center gap-3">
      <button
        className="btn-primary"
        onClick={apply}
        disabled={!form.start_date || !form.end_date}
      >
        Submit request
      </button>

      {msg && <span className="text-sm text-slate-600">{msg}</span>}
    </div>
  </div>

  {/* Manager Pending */}
  {isMgr && pending.length > 0 && (
    <div className="card">
      <h2 className="font-semibold mb-3">Pending approvals</h2>

      {pending.map((p) => (
        <div
          key={p.id}
          className="flex flex-wrap items-center justify-between gap-2 border-t border-slate-100 py-2 text-sm"
        >
          <span>
            Employee #{p.employee_id}: {p.start_date} → {p.end_date} ({p.days}d)
            {p.reason && ` — ${p.reason}`}
          </span>

          <span className="space-x-2">
            <button
              className="btn-primary !py-1"
              onClick={() => review(p.id, true)}
            >
              Approve
            </button>

            <button
              className="btn-ghost !py-1"
              onClick={() => review(p.id, false)}
            >
              Reject
            </button>
          </span>
        </div>
      ))}
    </div>
  )}

  {/* My Leaves */}
  <div className="card p-0 overflow-x-auto">
    <table className="w-full">
      <thead>
        <tr>
          <th className="th">From</th>
          <th className="th">To</th>
          <th className="th">Days</th>
          <th className="th">Status</th>
          <th className="th"></th>
        </tr>
      </thead>

      <tbody>
        {mine.map((m) => (
          <tr key={m.id}>
            <td className="td font-mono">{m.start_date}</td>
            <td className="td font-mono">{m.end_date}</td>
            <td className="td">{m.days}</td>
            <td className="td capitalize">{m.status}</td>
            <td className="td">
              {m.status === 'pending' && (
                <button
                  className="text-xs text-red-600 hover:underline"
                  onClick={() => cancelLeave(m.id)}
                >
                  Cancel
                </button>
              )}
            </td>
          </tr>
        ))}

        {mine.length === 0 && (
          <tr>
            <td className="td text-slate-500" colSpan={5}>
              No requests yet.
            </td>
          </tr>
        )}
      </tbody>
    </table>
  </div>
</div>

)
}


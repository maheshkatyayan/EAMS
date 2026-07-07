import { useEffect, useState } from 'react'
import { api } from '../lib/api'
import { useAuth, atLeast } from '../store/auth'

const empty = { emp_code: '', email: '', password: '', first_name: '', last_name: '', role: 'employee', designation: '', department_id: null as number | null, manager_id: null as number | null }

export default function Employees() {
  const { user } = useAuth()
  const isHr = atLeast(user?.role, 'hr')
  const [rows, setRows] = useState<any[]>([])
  const [deps, setDeps] = useState<any[]>([])
  const [q, setQ] = useState('')
  const [form, setForm] = useState({ ...empty })
  const [show, setShow] = useState(false)
  const [msg, setMsg] = useState('')

  const load = async () => {
    setRows((await api.get('/employees', { params: q ? { q } : {} })).data)
    setDeps((await api.get('/departments')).data)
  }
  useEffect(() => { load() }, [q])

  const create = async () => {
    setMsg('')
    try { await api.post('/employees', form); setShow(false); setForm({ ...empty }); load() }
    catch (e: any) { setMsg(e.response?.data?.detail ?? 'Failed') }
  }
  const toggle = async (r: any) => { await api.patch(`/employees/${r.id}`, { is_active: !r.is_active }); load() }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="font-display text-2xl font-bold">Employees</h1>
        <div className="flex gap-2">
          <input className="input w-56" placeholder="Search name or code" value={q} onChange={(e) => setQ(e.target.value)} />
          {isHr && <button className="btn-primary" onClick={() => setShow(!show)}>{show ? 'Close' : 'Add employee'}</button>}
        </div>
      </div>

      {show && (
        <div className="card grid sm:grid-cols-3 gap-3">
          <input className="input" placeholder="Code (EMP004)" value={form.emp_code} onChange={(e) => setForm({ ...form, emp_code: e.target.value })} />
          <input className="input" placeholder="Email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
          <input className="input" placeholder="Temp password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
          <input className="input" placeholder="First name" value={form.first_name} onChange={(e) => setForm({ ...form, first_name: e.target.value })} />
          <input className="input" placeholder="Last name" value={form.last_name} onChange={(e) => setForm({ ...form, last_name: e.target.value })} />
          <input className="input" placeholder="Designation" value={form.designation} onChange={(e) => setForm({ ...form, designation: e.target.value })} />
          <select className="input" value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })}>
            {['employee', 'manager', 'hr', 'super_admin'].map((r) => <option key={r}>{r}</option>)}
          </select>
          <select className="input" value={form.department_id ?? ''} onChange={(e) => setForm({ ...form, department_id: e.target.value ? +e.target.value : null })}>
            <option value="">No department</option>
            {deps.map((d) => <option key={d.id} value={d.id}>{d.name}</option>)}
          </select>
          <select className="input" value={form.manager_id ?? ''} onChange={(e) => setForm({ ...form, manager_id: e.target.value ? +e.target.value : null })}>
            <option value="">No manager</option>
            {rows.map((r) => <option key={r.id} value={r.id}>{r.first_name} {r.last_name}</option>)}
          </select>
          <div className="sm:col-span-3 flex items-center gap-3">
            <button className="btn-primary" onClick={create}>Create</button>
            {msg && <span className="text-sm text-red-600">{msg}</span>}
          </div>
        </div>
      )}

      <div className="card p-0 overflow-x-auto">
        <table className="w-full">
          <thead><tr><th className="th">Code</th><th className="th">Name</th><th className="th">Email</th><th className="th">Role</th><th className="th">Active</th>{isHr && <th className="th"></th>}</tr></thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.id} className={r.is_active ? '' : 'opacity-50'}>
                <td className="td font-mono">{r.emp_code}</td>
                <td className="td">{r.first_name} {r.last_name}</td>
                <td className="td">{r.email}</td>
                <td className="td capitalize">{r.role.replace('_', ' ')}</td>
                <td className="td">{r.is_active ? 'Yes' : 'No'}</td>
                {isHr && <td className="td"><button className="text-xs text-teal hover:underline" onClick={() => toggle(r)}>{r.is_active ? 'Deactivate' : 'Activate'}</button></td>}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

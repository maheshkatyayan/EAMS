import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Protected from './components/Protected'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Attendance from './pages/Attendance'
import Leaves from './pages/Leaves'
import Employees from './pages/Employees'
import Reports from './pages/Reports'
import Audit from './pages/Audit'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route element={<Protected><Layout /></Protected>}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/attendance" element={<Attendance />} />
          <Route path="/leaves" element={<Leaves />} />
          <Route path="/employees" element={<Protected min="manager"><Employees /></Protected>} />
          <Route path="/reports" element={<Protected min="manager"><Reports /></Protected>} />
          <Route path="/audit" element={<Protected min="super_admin"><Audit /></Protected>} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

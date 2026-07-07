import { Navigate } from 'react-router-dom'
import { useAuth, atLeast, Role } from '../store/auth'

export default function Protected({ min = 'employee', children }: { min?: Role; children: React.ReactNode }) {
  const { access, user } = useAuth()
  if (!access) return <Navigate to="/login" replace />
  if (!atLeast(user?.role, min)) return <Navigate to="/" replace />
  return <>{children}</>
}

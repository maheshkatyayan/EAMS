import axios from 'axios'
import { useAuth } from '../store/auth'
// const baseURL = 'http://localhost:8000/api/v1'
export const api = axios.create({ baseURL: 'http://localhost:8000/api/v1' })

api.interceptors.request.use((cfg) => {
  const t = useAuth.getState().access
  if (t) cfg.headers.Authorization = `Bearer ${t}`
  return cfg
})

let refreshing: Promise<void> | null = null

api.interceptors.response.use(undefined, async (err) => {
  const orig = err.config
  const { refresh, setTokens, logout } = useAuth.getState()
  if (err.response?.status === 401 && refresh && !orig._retried) {
    orig._retried = true
    refreshing ??= axios
      .post('/api/v1/auth/refresh', { refresh_token: refresh })
      .then((r) => setTokens(r.data.access_token, r.data.refresh_token))
      .catch(() => logout())
      .finally(() => { refreshing = null })
    await refreshing
    if (useAuth.getState().access) return api(orig)
  }
  return Promise.reject(err)
})

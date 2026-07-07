import { useEffect } from 'react'
import { useAuth } from '../store/auth'

export function useLiveEvents(onEvent: (e: any) => void) {
  const access = useAuth((s) => s.access)
  useEffect(() => {
    if (!access) return
    const proto = location.protocol === 'https:' ? 'wss' : 'ws'
    const ws = new WebSocket(`${proto}://${location.host}/api/v1/ws?token=${access}`)
    ws.onmessage = (m) => onEvent(JSON.parse(m.data))
    const ping = setInterval(() => ws.readyState === 1 && ws.send('ping'), 25000)
    return () => { clearInterval(ping); ws.close() }
  }, [access])
}

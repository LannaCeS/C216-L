import { useEffect, useState } from 'react'
import { Login } from './pages/Login'
import { Home } from './pages/Home'

const TEN_MINUTES_MS = 600000
const EXPIRES_AT_KEY = 'session_expires_at'

function getRemainingTime(): number {
  //para manter a sessão ativa por 10 minutos, mesmo que o usuário feche o navegador e abra novamente
  const saved = localStorage.getItem(EXPIRES_AT_KEY)
  if (!saved) return 0

  const remaining = Number(saved) - Date.now()
  return remaining > 0 ? remaining : 0
}

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(() => {
    return getRemainingTime() > 0
  })

  function handleLoginSuccess() {
    const expiresAt = Date.now() + TEN_MINUTES_MS
    localStorage.setItem(EXPIRES_AT_KEY, String(expiresAt))
    setIsAuthenticated(true)
  }

  function handleLogout() {
    localStorage.removeItem(EXPIRES_AT_KEY)
    setIsAuthenticated(false)
  }

  useEffect(() => {
    if (!isAuthenticated) return

    const remaining = getRemainingTime()

    if (remaining <= 0) {
      handleLogout()
      return
    }

    // agendar o logout exatamente para o tempo que falta
    const timer = setTimeout(() => {
      handleLogout()
    }, remaining)

    return () => clearTimeout(timer)
  }, [isAuthenticated])

  if (!isAuthenticated) {
    return <Login onLoginSuccess={handleLoginSuccess} />
  }

  return <Home onLogout={handleLogout} />
}

export default App
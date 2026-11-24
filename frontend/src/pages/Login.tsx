import { useState } from 'react'

interface LoginProps {
  onLoginSuccess: () => void
}

export function Login({ onLoginSuccess }: LoginProps) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const response = await fetch('http://localhost:8000/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      })

      if (!response.ok) {
        setError('Invalid email or password.')
        return
      }

      onLoginSuccess()
    } catch {
      setError('Could not connect to the backend.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <section id="center">
      <div>
        <h1>Books rater</h1>
        <p>Sign in to access your personal library.</p>
      </div>

      <form onSubmit={handleSubmit}>
        {error && <p>{error}</p>}

        <div>
          <label htmlFor="login-email">Email:</label>
          <input
            id="login-email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>

        <div>
          <label htmlFor="login-password">Password:</label>
          <input
            id="login-password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        <button type="submit" className="counter" disabled={loading} style={{ marginTop: '1rem' }}>
        {loading ? 'Signing in...' : 'Sign in'}
        </button>
      </form>
    </section>
  )
}
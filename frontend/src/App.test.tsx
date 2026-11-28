import { act, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, beforeEach, expect, test, vi } from 'vitest'
import App from './App'

vi.mock('./pages/Login', () => ({
  Login: ({ onLoginSuccess }: { onLoginSuccess: () => void }) => (
    <button onClick={onLoginSuccess}>fake-login</button>
  ),
}))

vi.mock('./pages/Home', () => ({
  Home: ({ onLogout }: { onLogout?: () => void }) => (
    <div>
      <p>home-page</p>
      <button onClick={onLogout}>fake-logout</button>
    </div>
  ),
}))

const KEY = 'session_expires_at'
const TEN_MINUTES = 600000

beforeEach(() => {
  localStorage.clear()
})

afterEach(() => {
  vi.useRealTimers()
})

test('sem sessão salva, mostra o login', () => {
  render(<App />)
  expect(screen.getByText('fake-login')).toBeInTheDocument()
})

test('login com sucesso mostra a home e grava a expiração', async () => {
  const user = userEvent.setup()
  render(<App />)

  await user.click(screen.getByText('fake-login'))

  expect(screen.getByText('home-page')).toBeInTheDocument()
  const expiresAt = Number(localStorage.getItem(KEY))
  expect(expiresAt).toBeGreaterThan(Date.now())
  expect(expiresAt).toBeLessThanOrEqual(Date.now() + TEN_MINUTES)
})

test('sessão válida salva entra direto na home', () => {
  localStorage.setItem(KEY, String(Date.now() + 5 * 60 * 1000))
  render(<App />)
  expect(screen.getByText('home-page')).toBeInTheDocument()
})

test('sessão expirada salva é ignorada e mostra o login', () => {
  localStorage.setItem(KEY, String(Date.now() - 1000))
  render(<App />)
  expect(screen.getByText('fake-login')).toBeInTheDocument()
})

test('botão sair limpa a sessão e volta ao login', async () => {
  const user = userEvent.setup()
  localStorage.setItem(KEY, String(Date.now() + TEN_MINUTES))
  render(<App />)

  await user.click(screen.getByText('fake-logout'))

  expect(screen.getByText('fake-login')).toBeInTheDocument()
  expect(localStorage.getItem(KEY)).toBeNull()
})

test('faz logout automático quando a sessão expira', () => {
  vi.useFakeTimers()
  localStorage.setItem(KEY, String(Date.now() + TEN_MINUTES))
  render(<App />)
  expect(screen.getByText('home-page')).toBeInTheDocument()

  act(() => {
    vi.advanceTimersByTime(TEN_MINUTES + 1)
  })

  expect(screen.getByText('fake-login')).toBeInTheDocument()
  expect(localStorage.getItem(KEY)).toBeNull()
})
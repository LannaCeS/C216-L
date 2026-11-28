import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, expect, test, vi } from 'vitest'
import { Login } from './Login'

afterEach(() => {
  vi.unstubAllGlobals()
})

async function fillAndSubmit(
  user: ReturnType<typeof userEvent.setup>,
  email = 'user@example.com',
  password = 'secret123'
) {
  await user.type(screen.getByLabelText('Email:'), email)
  await user.type(screen.getByLabelText('Password:'), password)
  await user.click(screen.getByRole('button', { name: /sign in/i }))
}

test('mostra os campos e o botão de entrar', () => {
  render(<Login onLoginSuccess={vi.fn()} />)

  expect(screen.getByLabelText('Email:')).toBeInTheDocument()
  expect(screen.getByLabelText('Password:')).toBeInTheDocument()
  expect(screen.getByRole('button', { name: 'Sign in' })).toBeEnabled()
})

test('envia email e senha ao backend e chama onLoginSuccess', async () => {
  const user = userEvent.setup()
  const onLoginSuccess = vi.fn()
  const fetchMock = vi.fn().mockResolvedValue({ ok: true })
  vi.stubGlobal('fetch', fetchMock)

  render(<Login onLoginSuccess={onLoginSuccess} />)
  await fillAndSubmit(user)

  expect(fetchMock).toHaveBeenCalledWith('http://localhost:8000/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email: 'user@example.com', password: 'secret123' }),
  })
  expect(onLoginSuccess).toHaveBeenCalledTimes(1)
})

test('credenciais inválidas mostram erro e não chamam onLoginSuccess', async () => {
  const user = userEvent.setup()
  const onLoginSuccess = vi.fn()
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: false, status: 401 }))

  render(<Login onLoginSuccess={onLoginSuccess} />)
  await fillAndSubmit(user, 'user@example.com', 'errada')

  expect(await screen.findByText('Invalid email or password.')).toBeInTheDocument()
  expect(onLoginSuccess).not.toHaveBeenCalled()
})

test('backend fora do ar mostra mensagem de conexão', async () => {
  const user = userEvent.setup()
  const onLoginSuccess = vi.fn()
  vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('Failed to fetch')))

  render(<Login onLoginSuccess={onLoginSuccess} />)
  await fillAndSubmit(user)

  expect(await screen.findByText('Could not connect to the backend.')).toBeInTheDocument()
  expect(onLoginSuccess).not.toHaveBeenCalled()
})

test('desabilita o botão enquanto a requisição está em andamento', async () => {
  const user = userEvent.setup()
  let resolveFetch!: (value: { ok: boolean }) => void
  vi.stubGlobal(
    'fetch',
    vi.fn(() => new Promise((resolve) => { resolveFetch = resolve }))
  )

  render(<Login onLoginSuccess={vi.fn()} />)
  await fillAndSubmit(user)

  const button = screen.getByRole('button', { name: 'Signing in...' })
  expect(button).toBeDisabled()

  resolveFetch({ ok: true })
  expect(await screen.findByRole('button', { name: 'Sign in' })).toBeEnabled()
})

test('limpa o erro anterior ao tentar de novo', async () => {
  const user = userEvent.setup()
  const fetchMock = vi
    .fn()
    .mockResolvedValueOnce({ ok: false })
    .mockResolvedValueOnce({ ok: true })
  vi.stubGlobal('fetch', fetchMock)

  render(<Login onLoginSuccess={vi.fn()} />)
  await fillAndSubmit(user)
  expect(await screen.findByText('Invalid email or password.')).toBeInTheDocument()

  await user.click(screen.getByRole('button', { name: 'Sign in' }))
  expect(screen.queryByText('Invalid email or password.')).not.toBeInTheDocument()
})
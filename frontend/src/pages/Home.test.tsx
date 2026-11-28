import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, expect, test, vi } from 'vitest'
import { Home } from './Home'

interface Book {
  id: number
  title: string
  author: string | null
  rating: number | null
  notes: string | null
}

function mockBackend(initial: Book[]) {
  let books = [...initial]
  const fetchMock = vi.fn(async (url: string, options?: RequestInit) => {
    const method = options?.method ?? 'GET'
    if (method === 'GET') return { ok: true, json: async () => books }
    if (method === 'POST') {
      const created = { id: 99, ...JSON.parse(options!.body as string) }
      books.push(created)
      return { ok: true, json: async () => created }
    }
    if (method === 'DELETE') {
      const id = Number(url.split('/').pop())
      books = books.filter((b) => b.id !== id)
      return { ok: true }
    }
    return { ok: false }
  })
  vi.stubGlobal('fetch', fetchMock)
  return fetchMock
}

const dom: Book = { id: 7, title: 'Dom Casmurro', author: null, rating: 5, notes: null }

afterEach(() => {
  vi.unstubAllGlobals()
  vi.restoreAllMocks()
})

test('lista os livros vindos do backend', async () => {
  mockBackend([dom])
  render(<Home />)
  expect(await screen.findByText('Dom Casmurro - 5 stars')).toBeInTheDocument()
})

test('cria um livro com título e nota', async () => {
  const user = userEvent.setup()
  const fetchMock = mockBackend([])
  render(<Home />)

  await user.type(screen.getByLabelText(/book title/i), 'Livro Novo')
  await user.click(screen.getByRole('button', { name: /your given rating/i }))
  await user.click(screen.getByRole('button', { name: /your given rating/i }))
  await user.click(screen.getByRole('button', { name: /send your rating/i }))

  expect(await screen.findByText('Livro Novo - 2 stars')).toBeInTheDocument()
  const post = fetchMock.mock.calls.find(([, o]) => o?.method === 'POST')!
  expect(JSON.parse(post[1]!.body as string)).toMatchObject({ title: 'Livro Novo', rating: 2 })
})

test('exclui o livro pelo título digitado, ignorando maiúsculas e espaços', async () => {
  const user = userEvent.setup()
  vi.spyOn(window, 'confirm').mockReturnValue(true)
  const fetchMock = mockBackend([dom])
  render(<Home />)
  await screen.findByText('Dom Casmurro - 5 stars')

  await user.type(screen.getByLabelText(/book title/i), '  dom casmurro ')
  await user.click(screen.getByRole('button', { name: /delete rating/i }))

  expect(fetchMock).toHaveBeenCalledWith('http://localhost:8000/books/7', { method: 'DELETE' })
  expect(screen.queryByText('Dom Casmurro - 5 stars')).not.toBeInTheDocument()
})

test('mostra erro ao excluir um título que não existe', async () => {
  const user = userEvent.setup()
  mockBackend([dom])
  render(<Home />)
  await screen.findByText('Dom Casmurro - 5 stars')

  await user.type(screen.getByLabelText(/book title/i), 'Inexistente')
  await user.click(screen.getByRole('button', { name: /delete rating/i }))

  expect(await screen.findByRole('alert')).toHaveTextContent('Book not found.')
})
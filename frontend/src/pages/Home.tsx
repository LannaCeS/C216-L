import { useEffect, useState, type FormEvent } from 'react'
import '../App.css'

interface Book {
  id: number
  title: string
  author: string | null
  rating: number | null
  notes: string | null
}

interface HomeProps {
  onLogout?: () => void
}

const API_URL = 'http://localhost:8000'

export function Home({ onLogout }: HomeProps) {
  const [books, setBooks] = useState<Book[]>([])
  const [title, setTitle] = useState('')
  const [author, setAuthor] = useState('')
  const [notes, setNotes] = useState('')
  const [rating, setRating] = useState(0)
  const [error, setError] = useState('')

  async function loadBooks() {
    // Carrega todos os livros presentes no BD
    const response = await fetch(`${API_URL}/books/`)
    if (!response.ok) throw new Error()
    setBooks(await response.json())
  }

  useEffect(() => {
    loadBooks().catch(() => setError('It was not possible to connect to the backend.'))
  }, [])

  function findByTitle(value: string) {
    //Pesquisa do livro na memória do react pelo seu título
    return books.find(
      (b) => b.title.trim().toLowerCase() === value.trim().toLowerCase()
    )
  }

  async function handleSubmit(e: FormEvent) {
    // Impede o envio do formulário e a atualização automática da página
    e.preventDefault()
    if (!title.trim()) {
      setError('Please enter the book title.')
      return
    }

    const data = {
      title: title.trim(),
      author: author.trim() || null,
      notes: notes.trim() || null,
      rating,
    }

    // Se o título já existe, atualiza com PATCH, senão, cria com POST
    const existing = findByTitle(title)
    const response = await fetch(
      existing ? `${API_URL}/books/${existing.id}` : `${API_URL}/books/`,
      {
        method: existing ? 'PATCH' : 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      }
    )

    if (!response.ok) {
      setError('It was not possible to save the book.')
      return
    }

    setTitle('')
    setAuthor('')
    setNotes('')
    setRating(0)
    setError('')
    await loadBooks()
  }

  async function handleDelete() {
    //Apaga um livro mediante confirmação do usuário
    const book = findByTitle(title)
    if (!book) {
      setError('Book not found.')
      return
    }
    if (!window.confirm(`Do you want to delete "${book.title}"?`)) return

    const response = await fetch(`${API_URL}/books/${book.id}`, {
      method: 'DELETE',
    })
    if (!response.ok) {
      setError('It was not possible to delete the book.')
      return
    }

    setTitle('')
    setError('')
    await loadBooks()
  }

  return (
    <>
      {onLogout && (
        <div style={{ display: 'flex', justifyContent: 'flex-end', padding: '1rem' }}>
          <button type="button" onClick={onLogout}>Logout</button>
        </div>
      )}

      <section id="center">
        <div className="hero"></div>
        <div>
          <h1>Books rater</h1>
          <p>Rate your favorite books and save them to your personal library.</p>
        </div>

        {error && <p role="alert">{error}</p>}

        <div>
          <p>Enter the book's information below:</p>
          <form id="book-form" onSubmit={handleSubmit}>
            <label htmlFor="book-title"> Book Title: </label>
            <input
              type="text"
              id="book-title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
            />
            <label htmlFor="book-author"> Book Author: </label>
            <input
              type="text"
              id="book-author"
              value={author}
              onChange={(e) => setAuthor(e.target.value)}
            />
            <label htmlFor="book-description"> Notes: </label>
            <textarea
              id="book-description"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
            />
          </form>
        </div>

        <div>
          <p>Increase stars by clicking the button!</p>
        </div>

        <button
          type="button"
          className="counter"
          onClick={() => setRating((r) => (r >= 5 ? 0 : r + 1))} // só vai até 5 estrelas, depois volta para 0
        >
          Your given rating is {rating} stars!
        </button>

        <button type="submit" form="book-form" className="counter">
          Send your rating
        </button>

        <button type="button" className="counter" onClick={handleDelete}>
          Delete rating
        </button>
      </section>

      <div className="ticks"></div>

      <section id="next-steps">
        <div id="docs">
          <h2>Notes</h2>
          <p>Little notes about the books you've rated.</p>
          <ul>
            {books.filter((b) => b.notes).map((b) => (
              <li key={b.id}>
                <p>{b.title} - "{b.notes}"</p>
              </li>
            ))}
          </ul>
        </div>

        <div id="social">
          <h2>My ratings</h2>
          <ul>
            {books.map((b) => (
              <li key={b.id}>
                <p>{b.title} - {b.rating ?? 0} stars</p>
              </li>
            ))}
          </ul>
        </div>
      </section>

      <div className="ticks"></div>
      <section id="spacer"></section>
    </>
  )
}
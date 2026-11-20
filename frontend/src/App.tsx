import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from './assets/vite.svg'
import './App.css'

function App() {
  const [count, setCount] = useState(0)

  return (
    <>
      <section id="center">
        <div className="hero">
        </div>
        <div>
          <h1>Books rater</h1>
          <p>
            Rate your favorite books and save them to your personal library.
          </p>
        </div>

        <div>
          <p>Enter the book's information bellow:</p>
          <form>
            <label htmlFor="book-title">  Book Title:  </label>
            <input type="text" id="book-title" name="book-title" />
            <label htmlFor="book-author">  Book Author:  </label>
            <input type="text" id="book-author" name="book-author" />
            <label htmlFor="book-description">  Notes:  </label>
            <textarea id="book-description" name="book-description"></textarea>
          </form>
        </div>
        <div>
          <p>Increase stars by clicking the button!</p>
        </div>
        <button
          type="button"
          className="counter"
          onClick={() => setCount((count) => count + 1)}
        >
          Your given rating is {count} stars!
        </button>

        <button
          type="button"
          className="counter"
          onClick={() => alert(`You have rated this book with ${count} stars!`)}
        >
          Send your rating
        </button>
      </section>

      <div className="ticks"></div>

      <section id="next-steps">
        <div id="docs">
          <h2>Notes</h2>
          <p>Little notes about the books you've rated.</p>
          <ul>
            <li>
              <p>book 1 - "This book was amazing!"</p>
            </li>
            <li>
              <p>book 2 - "This book was okay."</p>
            </li>
          </ul>
        </div>
        <div id="social">
          <h2>My ratings</h2>
          <ul>
            <li>
              <p>book 1 - 5 stars</p>
            </li>
            <li>
              <p>book 2 - 4 stars</p>
            </li>
            <li>
              <p>book 3 - 3 stars</p>
            </li>
            <li>
              <p>book 4 - 2 stars</p>
            </li>
          </ul>
        </div>
      </section>

      <div className="ticks"></div>
      <section id="spacer"></section>
    </>
  )
}

export default App

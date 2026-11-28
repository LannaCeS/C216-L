import { test, expect, type Page } from '@playwright/test'

const EMAIL = process.env.SINGLE_USER_EMAIL ?? 'usuario@exemplo.com'
const PASSWORD = process.env.SINGLE_USER_PASSWORD ?? 'senha_valida'

async function login(page: Page) {
  await page.goto('/')
  await page.getByLabel('Email:').fill(EMAIL)
  await page.getByLabel('Password:').fill(PASSWORD)
  await page.getByRole('button', { name: 'Sign in' }).click()
  await expect(page.getByLabel(/book title/i)).toBeVisible()
}

test('cria, atualiza e exclui um livro', async ({ page }) => {
  const title = `Livro E2E ${Date.now()}`
  const author = 'Test'
  const notes = 'note'
  await login(page)

  // cria com 2 estrelas
  await page.getByLabel(/book title/i).fill(title)
  await page.getByLabel(/book author/i).fill(author)
  await page.getByLabel(/notes/i).fill(notes)
  await page.getByRole('button', { name: /your given rating/i }).click()
  await page.getByRole('button', { name: /your given rating/i }).click()
  await page.getByRole('button', { name: /send your rating/i }).click()
  await expect(page.getByText(`${title} - 2 stars`)).toBeVisible()

  // mesmo título + 4 estrelas
  await page.getByLabel(/book title/i).fill(title)
  for (let i = 0; i < 4; i++) {
    await page.getByRole('button', { name: /your given rating/i }).click()
  }
  await page.getByRole('button', { name: /send your rating/i }).click()
  await expect(page.getByText(`${title} - 4 stars`)).toBeVisible()
  await expect(page.getByText(title)).toHaveCount(1) // sem duplicação

  // exclui pelo título digitado
  page.once('dialog', (dialog) => dialog.accept())
  await page.getByLabel(/book title/i).fill(title)
  await page.getByRole('button', { name: /delete rating/i }).click()
  await expect(page.getByText(title)).toHaveCount(0)
})

test('a sessão continua após recarregar a página', async ({ page }) => {
  await login(page)
  await page.reload()
  await expect(page.getByLabel(/book title/i)).toBeVisible()
})
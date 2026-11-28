import { test, expect } from '@playwright/test'

const EMAIL = process.env.SINGLE_USER_EMAIL ?? 'usuario@exemplo.com'
const PASSWORD = process.env.SINGLE_USER_PASSWORD ?? 'senha_valida'

test('login com credenciais corretas abre a home', async ({ page }) => {
  await page.goto('/')

  await page.getByLabel('Email:').fill(EMAIL)
  await page.getByLabel('Password:').fill(PASSWORD)
  await page.getByRole('button', { name: 'Sign in' }).click()

  await expect(page.getByRole('button', { name: 'Logout' })).toBeVisible()
})

test('login com senha errada mostra erro', async ({ page }) => {
  await page.goto('/')

  await page.getByLabel('Email:').fill(EMAIL)
  await page.getByLabel('Password:').fill('senha-errada')
  await page.getByRole('button', { name: 'Sign in' }).click()

  await expect(page.getByText('Invalid email or password.')).toBeVisible()
})

test('login com e-mail errado mostra erro', async ({ page }) => {
  await page.goto('/')

  await page.getByLabel('Email:').fill('email@teste.com')
  await page.getByLabel('Password:').fill(PASSWORD)
  await page.getByRole('button', { name: 'Sign in' }).click()

  await expect(page.getByText('Invalid email or password.')).toBeVisible()
})
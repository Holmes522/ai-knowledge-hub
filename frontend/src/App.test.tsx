import { render, screen } from '@testing-library/react'
import { vi } from 'vitest'
import App from './App'

vi.mock('./api', () => ({
  me: vi.fn().mockRejectedValue(new Error('not signed in')),
  login: vi.fn(),
  register: vi.fn(),
  listNotes: vi.fn(),
  createNote: vi.fn(),
  updateNote: vi.fn(),
  deleteNote: vi.fn(),
  logout: vi.fn(),
}))

test('shows the knowledge hub sign-in screen by default', async () => {
  render(<App />)
  expect(await screen.findByRole('heading', { name: '欢迎回来。' })).toBeInTheDocument()
  expect(screen.getByRole('button', { name: '登录' })).toBeInTheDocument()
})

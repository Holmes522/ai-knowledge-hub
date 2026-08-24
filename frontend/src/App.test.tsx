import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { vi } from 'vitest'
import App from './App'
import { listNotes, me, register } from './api'
import type { User } from './types'

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

test('does not crash when a stale session returns an invalid user payload', async () => {
  vi.mocked(me).mockResolvedValueOnce({} as User)
  render(<App />)
  expect(await screen.findByRole('heading', { name: '欢迎回来。' })).toBeInTheDocument()
})

test('registers a new learner and opens the knowledge space', async () => {
  const registeredUser: User = {
    id: 1,
    username: 'new_learner',
    email: 'new_learner@example.com',
    role: 'user',
  }
  vi.mocked(register).mockResolvedValueOnce(registeredUser)
  vi.mocked(listNotes).mockResolvedValueOnce({ items: [], total: 0 })
  const user = userEvent.setup()

  render(<App />)
  await user.click(await screen.findByRole('button', { name: '注册' }))
  await user.type(screen.getByRole('textbox', { name: '用户名' }), 'new_learner')
  await user.type(screen.getByRole('textbox', { name: '邮箱' }), 'new_learner@example.com')
  await user.type(screen.getByLabelText('密码'), 'Password123!')
  await user.click(screen.getByRole('button', { name: '创建我的空间' }))

  expect(await screen.findByText('new_learner')).toBeInTheDocument()
  expect(register).toHaveBeenCalledWith('new_learner', 'new_learner@example.com', 'Password123!')
})

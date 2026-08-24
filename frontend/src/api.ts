import axios from 'axios'
import type { Note, NoteInput, NoteStatus, User } from './types'

const api = axios.create({ baseURL: import.meta.env.VITE_API_URL ?? 'http://localhost:8000' })

api.interceptors.request.use((config) => {
  const token = sessionStorage.getItem('knowledge_hub_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

export async function login(username: string, password: string) {
  const body = new URLSearchParams({ username, password })
  const { data } = await api.post<{ access_token: string }>('/api/auth/login', body)
  sessionStorage.setItem('knowledge_hub_token', data.access_token)
  return me()
}

export async function register(username: string, email: string, password: string) {
  await api.post('/api/auth/register', { username, email, password })
  return login(username, password)
}

export async function me() {
  const { data } = await api.get<User>('/api/auth/me')
  return data
}

export async function listNotes(query = '') {
  const { data } = await api.get<{ items: Note[]; total: number }>('/api/notes', { params: { q: query || undefined } })
  return data
}

export async function createNote(input: NoteInput) {
  const { data } = await api.post<Note>('/api/notes', input)
  return data
}

export async function updateNote(id: number, input: Partial<NoteInput> & { status?: NoteStatus }) {
  const { data } = await api.patch<Note>(`/api/notes/${id}`, input)
  return data
}

export async function deleteNote(id: number) {
  await api.delete(`/api/notes/${id}`)
}

export function logout() {
  sessionStorage.removeItem('knowledge_hub_token')
}

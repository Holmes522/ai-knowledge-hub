export type User = {
  id: number
  username: string
  email: string
  role: string
}

export type Tag = {
  id: number
  name: string
  type: string
}

export type NoteStatus = 'unlearned' | 'learning' | 'completed' | 'reviewing'

export type Note = {
  id: number
  title: string
  summary: string
  content: string
  status: NoteStatus
  views: number
  is_public: boolean
  created_time: string
  updated_time: string
  tags: Tag[]
}

export type NoteInput = {
  title: string
  summary: string
  content: string
  tags: string[]
}

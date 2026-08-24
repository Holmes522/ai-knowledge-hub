import { FormEvent, useEffect, useMemo, useState } from 'react'
import { BookOpen, Check, ChevronRight, LogOut, Plus, Search, Sparkles, Trash2 } from 'lucide-react'
import * as api from './api'
import type { Note, NoteInput, NoteStatus, User } from './types'
import type { FileAttachment } from './types'
import { Attachments } from './components/Attachments'
import { AIAssistant } from './components/AIAssistant'

const statusLabels: Record<NoteStatus, string> = {
  unlearned: '未学习',
  learning: '学习中',
  completed: '已完成',
  reviewing: '复习中',
}

const emptyDraft: NoteInput = { title: '', summary: '', content: '', tags: [] }

function App() {
  const [user, setUser] = useState<User | null>(null)
  const [authChecked, setAuthChecked] = useState(false)
  const [authMode, setAuthMode] = useState<'login' | 'register'>('login')
  const [authForm, setAuthForm] = useState({ username: '', email: '', password: '' })
  const [authError, setAuthError] = useState('')
  const [notes, setNotes] = useState<Note[]>([])
  const [selectedId, setSelectedId] = useState<number | null>(null)
  const [draft, setDraft] = useState<NoteInput>(emptyDraft)
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [notice, setNotice] = useState('')
  const [files, setFiles] = useState<FileAttachment[]>([])

  const selected = useMemo(() => notes.find((note) => note.id === selectedId) ?? null, [notes, selectedId])

  useEffect(() => {
    api.me().then(setUser).catch(() => undefined).finally(() => setAuthChecked(true))
  }, [])

  useEffect(() => {
    if (!user) return
    api.listNotes(query).then(({ items }) => {
      setNotes(items)
      if (selectedId && !items.some((note) => note.id === selectedId)) setSelectedId(null)
    })
  }, [user, query])

  useEffect(() => {
    if (selected) {
      setDraft({ title: selected.title, summary: selected.summary, content: selected.content, tags: selected.tags.map((tag) => tag.name) })
    } else setDraft(emptyDraft)
  }, [selectedId])

  useEffect(() => {
    if (!selectedId) {
      setFiles([])
      return
    }
    api.listFiles(selectedId).then(setFiles).catch(() => setFiles([]))
  }, [selectedId])

  async function submitAuth(event: FormEvent) {
    event.preventDefault()
    setAuthError('')
    try {
      const nextUser = authMode === 'login'
        ? await api.login(authForm.username, authForm.password)
        : await api.register(authForm.username, authForm.email, authForm.password)
      setUser(nextUser)
    } catch (error) {
      setAuthError('登录信息无效，请检查后重试。')
    }
  }

  async function saveNote(event: FormEvent) {
    event.preventDefault()
    if (!draft.title.trim()) return
    setLoading(true)
    try {
      const saved = selected ? await api.updateNote(selected.id, draft) : await api.createNote(draft)
      setNotes((current) => selected ? current.map((note) => note.id === saved.id ? saved : note) : [saved, ...current])
      setSelectedId(saved.id)
      setNotice('笔记已保存')
      window.setTimeout(() => setNotice(''), 2000)
    } finally {
      setLoading(false)
    }
  }

  async function changeStatus(status: NoteStatus) {
    if (!selected) return
    const saved = await api.updateNote(selected.id, { status })
    setNotes((current) => current.map((note) => note.id === saved.id ? saved : note))
  }

  async function removeNote() {
    if (!selected || !window.confirm('确定删除这篇笔记吗？')) return
    await api.deleteNote(selected.id)
    setNotes((current) => current.filter((note) => note.id !== selected.id))
    setSelectedId(null)
  }

  async function addFile(file: File) {
    if (!selected) return
    const attachment = await api.uploadFile(selected.id, file)
    setFiles((current) => [attachment, ...current])
    setNotice('附件已上传')
  }

  async function removeFile(fileId: number) {
    if (!selected) return
    await api.deleteFile(selected.id, fileId)
    setFiles((current) => current.filter((file) => file.id !== fileId))
  }

  if (!authChecked) return <div className="loading-screen">正在打开你的知识空间…</div>
  if (!user) return <AuthScreen mode={authMode} form={authForm} error={authError} onModeChange={setAuthMode} onChange={setAuthForm} onSubmit={submitAuth} />

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand"><span className="brand-mark"><Sparkles size={16} /></span><span>AI Knowledge Hub</span></div>
        <div className="workspace-label">我的学习空间</div>
        <nav className="nav-list"><button className="nav-item active"><BookOpen size={17} /> 所有笔记 <span>{notes.length}</span></button></nav>
        <div className="sidebar-bottom"><div className="user-chip"><div className="avatar">{user.username[0].toUpperCase()}</div><div><strong>{user.username}</strong><small>{user.role === 'admin' ? '管理员' : '学习者'}</small></div></div><button className="icon-button" title="退出登录" onClick={() => { api.logout(); setUser(null) }}><LogOut size={17} /></button></div>
      </aside>
      <main className="main-area">
        <header className="topbar"><div><p className="eyebrow">PERSONAL KNOWLEDGE OS</p><h1>把学过的，变成自己的。</h1></div><button className="primary-button" onClick={() => setSelectedId(null)}><Plus size={17} /> 新建笔记</button></header>
        <div className="content-grid">
          <section className="notes-panel"><div className="panel-heading"><div><h2>笔记库</h2><p>{notes.length} 篇学习记录</p></div><div className="search-box"><Search size={16} /><input aria-label="搜索笔记" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="搜索标题、内容或标签" /></div></div><div className="note-list">{notes.length === 0 ? <div className="empty-state"><div className="empty-icon"><BookOpen size={22} /></div><h3>从一篇笔记开始</h3><p>记录今天新学到的东西，建立你的知识网络。</p><button className="text-button" onClick={() => setSelectedId(null)}>创建第一篇 <ChevronRight size={15} /></button></div> : notes.map((note) => <button key={note.id} className={`note-card ${selectedId === note.id ? 'selected' : ''}`} onClick={() => setSelectedId(note.id)}><div className="note-card-top"><span className={`status-dot ${note.status}`} /><span>{statusLabels[note.status]}</span><time>{new Date(note.updated_time).toLocaleDateString('zh-CN')}</time></div><h3>{note.title}</h3><p>{note.summary || note.content.slice(0, 80) || '暂无摘要'}</p><div className="tag-row">{note.tags.slice(0, 3).map((tag) => <span key={tag.id} className="tag">{tag.name}</span>)}</div></button>)}</div></section>
          <section className="editor-panel"><div className="editor-heading"><div><span className="editor-kicker">{selected ? 'EDIT NOTE' : 'NEW NOTE'}</span><h2>{selected ? '继续完善这份知识' : '捕捉一个新想法'}</h2></div>{selected && <button className="danger-button" onClick={removeNote}><Trash2 size={16} /> 删除</button>}</div><form className="note-form" onSubmit={saveNote}><input className="title-input" aria-label="笔记标题" value={draft.title} onChange={(event) => setDraft({ ...draft, title: event.target.value })} placeholder="笔记标题" /><input className="summary-input" aria-label="笔记摘要" value={draft.summary} onChange={(event) => setDraft({ ...draft, summary: event.target.value })} placeholder="写一句摘要，帮助未来的你快速回忆" /><textarea className="content-input" aria-label="笔记正文" value={draft.content} onChange={(event) => setDraft({ ...draft, content: event.target.value })} placeholder="用 Markdown 记录你的思考…" /><input className="tag-input" aria-label="笔记标签" value={draft.tags.join(', ')} onChange={(event) => setDraft({ ...draft, tags: event.target.value.split(',').map((tag) => tag.trim()).filter(Boolean) })} placeholder="标签，用逗号分隔" />{selected && <Attachments files={files} onUpload={addFile} onDelete={removeFile} />}<div className="editor-footer"><div className="status-picker">{(['unlearned', 'learning', 'completed', 'reviewing'] as NoteStatus[]).map((status) => <button type="button" key={status} className={selected?.status === status ? 'status-button active' : 'status-button'} onClick={() => changeStatus(status)}><span className={`status-dot ${status}`} />{statusLabels[status]}{selected?.status === status && <Check size={14} />}</button>)}</div><button className="save-button" disabled={loading}>{loading ? '保存中…' : '保存笔记'}</button></div></form>{selected && <AIAssistant noteId={selected.id} />}</section>
        </div>
      </main>
      {notice && <div className="toast">{notice}</div>}
    </div>
  )
}

function AuthScreen({ mode, form, error, onModeChange, onChange, onSubmit }: { mode: 'login' | 'register'; form: { username: string; email: string; password: string }; error: string; onModeChange: (mode: 'login' | 'register') => void; onChange: (form: { username: string; email: string; password: string }) => void; onSubmit: (event: FormEvent) => void }) {
  return <div className="auth-shell"><div className="auth-art"><div className="orb orb-one" /><div className="orb orb-two" /><span className="brand-mark large"><Sparkles size={21} /></span><p className="art-quote">“The palest ink is better than the best memory.”</p><span className="art-caption">— 学习者的第二大脑</span></div><form className="auth-card" onSubmit={onSubmit}><p className="eyebrow">YOUR LEARNING SPACE</p><h1>欢迎回来。</h1><p className="auth-intro">把零散的输入，整理成可回看的知识。</p><div className="auth-tabs"><button type="button" className={mode === 'login' ? 'active' : ''} onClick={() => onModeChange('login')}>登录</button><button type="button" className={mode === 'register' ? 'active' : ''} onClick={() => onModeChange('register')}>注册</button></div><label>用户名<input required value={form.username} onChange={(event) => onChange({ ...form, username: event.target.value })} /></label>{mode === 'register' && <label>邮箱<input required type="email" value={form.email} onChange={(event) => onChange({ ...form, email: event.target.value })} /></label>}<label>密码<input required type="password" minLength={8} value={form.password} onChange={(event) => onChange({ ...form, password: event.target.value })} /></label>{error && <p className="form-error">{error}</p>}<button className="auth-submit">{mode === 'login' ? '进入知识空间' : '创建我的空间'} <ChevronRight size={17} /></button></form></div>
}

export default App

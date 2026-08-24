import { FormEvent, useState } from 'react'
import { BrainCircuit, Database, Send } from 'lucide-react'
import * as api from '../api'

export function AIAssistant({ noteId }: { noteId: number }) {
  const [question, setQuestion] = useState('')
  const [answer, setAnswer] = useState('')
  const [sourceTitle, setSourceTitle] = useState('')
  const [notice, setNotice] = useState('')

  async function index() {
    const result = await api.indexNote(noteId)
    setNotice(`已建立 ${result.chunks} 个知识片段的索引`)
  }

  async function ask(event: FormEvent) {
    event.preventDefault()
    if (!question.trim()) return
    const result = await api.askAI(question)
    setAnswer(result.answer)
    setSourceTitle(result.sources[0]?.title ?? '')
  }

  return <section className="ai-assistant" aria-label="AI 学习助手"><div className="ai-heading"><div><span className="editor-kicker">AI STUDY ASSISTANT</span><h3><BrainCircuit size={17} /> 从你的笔记里回答</h3></div><button type="button" className="index-button" onClick={() => void index()}><Database size={13} /> 建立索引</button></div>{notice && <p className="ai-notice">{notice}</p>}<form className="ai-form" onSubmit={ask}><input aria-label="向 AI 提问" value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="例如：我之前学过 RAG 吗？" /><button aria-label="发送问题"><Send size={14} /></button></form>{answer && <div className="ai-answer"><p>{answer}</p>{sourceTitle && <small>来源：{sourceTitle}</small>}</div>}</section>
}

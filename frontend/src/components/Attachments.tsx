import { FileText, Paperclip, Trash2, Upload } from 'lucide-react'
import type { FileAttachment } from '../types'

const apiOrigin = import.meta.env.VITE_API_URL ?? window.location.origin

export function Attachments({ files, onUpload, onDelete }: { files: FileAttachment[]; onUpload: (file: File) => Promise<void>; onDelete: (fileId: number) => Promise<void> }) {
  return <section className="attachments" aria-label="笔记附件"><div className="attachments-heading"><span><Paperclip size={14} /> 附件 {files.length > 0 && `· ${files.length}`}</span><label className="upload-button"><Upload size={13} /> 上传<input type="file" onChange={(event) => { const file = event.target.files?.[0]; if (file) void onUpload(file); event.target.value = '' }} /></label></div>{files.length > 0 && <ul className="attachment-list">{files.map((file) => <li key={file.id}><FileText size={14} /><a href={`${apiOrigin}${file.file_url}`} target="_blank" rel="noreferrer">{file.filename}</a><span className="file-size">{formatSize(file.file_size)}</span><button type="button" title={`删除 ${file.filename}`} onClick={() => void onDelete(file.id)}><Trash2 size={13} /></button></li>)}</ul>}</section>
}

function formatSize(bytes: number) {
  if (bytes < 1024) return `${bytes} B`
  return `${(bytes / 1024).toFixed(bytes < 1024 * 100 ? 1 : 0)} KB`
}

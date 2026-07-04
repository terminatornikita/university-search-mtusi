import { useState, useRef, ChangeEvent } from 'react'
import axios from 'axios'

interface Props {
  onUpload: () => void
}

export default function UploadZone({ onUpload }: Props) {
  const [status, setStatus] = useState<'idle' | 'uploading' | 'done' | 'error'>('idle')
  const inputRef = useRef<HTMLInputElement>(null)

  const handleFiles = async (files: FileList | null) => {
    if (!files) return
    for (const file of Array.from(files)) {
      setStatus('uploading')
      const form = new FormData()
      form.append('file', file)
      try {
        await axios.post('/api/v1/documents/upload', form)
        setStatus('done')
        onUpload()
      } catch (err: any) {
        setStatus('error')
        alert(err.response?.data?.detail || 'Ошибка загрузки')
      }
    }
  }

  return (
    <div style={{
      border: '2px dashed #ccc',
      borderRadius: 12,
      padding: 40,
      textAlign: 'center',
      marginBottom: 30,
      background: '#fafafa'
    }}>
      <input
        type="file"
        multiple
        accept=".pdf,.docx"
        style={{ display: 'none' }}
        ref={inputRef}
        onChange={(e: ChangeEvent<HTMLInputElement>) => handleFiles(e.target.files)}
      />
      <button
        onClick={() => inputRef.current?.click()}
        disabled={status === 'uploading'}
        style={{ padding: '12px 24px', fontSize: 16, cursor: 'pointer' }}
      >
        {status === 'uploading' ? 'Загрузка...' : status === 'done' ? 'Готово' : status === 'error' ? 'Ошибка' : 'Выбрать файлы (PDF, DOCX)'}
      </button>
      <p style={{ color: '#666', marginTop: 10 }}>
        Перетащите файлы сюда или нажмите на кнопку
      </p>
    </div>
  )
}

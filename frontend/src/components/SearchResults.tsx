import { useState } from 'react'
import axios from 'axios'

interface Result {
  chunk_id: string
  file_name: string
  page: number
  text: string
  highlight: string
  score: number
}

export default function SearchResults() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<Result[]>([])
  const [loading, setLoading] = useState(false)

  const search = async () => {
    if (!query.trim()) return
    setLoading(true)
    try {
      const res = await axios.get(`/api/v1/search?q=${encodeURIComponent(query)}`)
      setResults(res.data.results)
    } catch {
      alert('Ошибка поиска')
    }
    setLoading(false)
  }

  return (
    <div>
      <h2>Поиск по документам</h2>
      <div style={{ display: 'flex', gap: 10, marginBottom: 20 }}>
        <input
          type="text"
          value={query}
          onChange={e => setQuery(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && search()}
          placeholder="Введите запрос..."
          style={{ flex: 1, padding: 12, fontSize: 16, borderRadius: 8, border: '1px solid #ccc' }}
        />
        <button onClick={search} disabled={loading} style={{ padding: '12px 24px', fontSize: 16 }}>
          {loading ? 'Поиск...' : 'Найти'}
        </button>
      </div>

      {results.length === 0 && query && !loading && (
        <p style={{ color: '#666' }}>По вашему запросу ничего не найдено. Попробуйте изменить формулировку</p>
      )}

      <div>
        {results.map(r => (
          <div key={r.chunk_id} style={{
            border: '1px solid #e0e0e0',
            borderRadius: 8,
            padding: 16,
            marginBottom: 12,
            background: '#fff',
            boxShadow: '0 1px 3px rgba(0,0,0,0.05)'
          }}>
            <div style={{ fontWeight: 600, marginBottom: 8, color: '#1565c0' }}>
              {r.file_name} (стр. {r.page}) — релевантность: {r.score.toFixed(2)}
            </div>
            <div
              style={{ lineHeight: 1.6, color: '#333' }}
              dangerouslySetInnerHTML={{
                __html: r.highlight || r.text
              }}
            />
          </div>
        ))}
      </div>
    </div>
  )
}

import { useState } from 'react'
import UploadZone from './components/UploadZone'
import SearchResults from './components/SearchResults'

function App() {
  const [refresh, setRefresh] = useState(0)

  return (
    <div style={{ maxWidth: 900, margin: '0 auto', padding: '20px', fontFamily: 'system-ui, sans-serif' }}>
      <h1 style={{ textAlign: 'center' }}>Поисковая система базы знаний МТУСИ</h1>
      <UploadZone onUpload={() => setRefresh(r => r + 1)} />
      <SearchResults />
    </div>
  )
}

export default App

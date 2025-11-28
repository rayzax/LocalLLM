import { useEffect, useState } from 'react'
import { api } from './services/api'
import type { HealthStatus, OllamaHealth } from './types'

function App() {
  const [health, setHealth] = useState<HealthStatus | null>(null)
  const [ollamaHealth, setOllamaHealth] = useState<OllamaHealth | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const healthData = await api.checkHealth()
        setHealth(healthData)

        try {
          const ollamaData = await api.checkOllamaHealth()
          setOllamaHealth(ollamaData)
        } catch (err) {
          console.error('Ollama health check failed:', err)
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to connect to API')
      }
    }

    checkHealth()
  }, [])

  return (
    <div className="min-h-screen bg-dark-950 flex items-center justify-center p-8">
      <div className="max-w-2xl w-full">
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold mb-4 text-gradient">
            LLMLocal
          </h1>
          <p className="text-gray-400 text-lg">
            Local LLM Dashboard - Foundation Setup Complete
          </p>
        </div>

        <div className="card space-y-4">
          <div>
            <h2 className="text-2xl font-semibold mb-4 text-primary-400">
              System Status
            </h2>
          </div>

          {error && (
            <div className="bg-red-900/20 border border-red-800 rounded-lg p-4">
              <p className="text-red-400">Error: {error}</p>
            </div>
          )}

          {health && (
            <div className="bg-green-900/20 border border-green-800 rounded-lg p-4">
              <p className="text-green-400">
                ✓ API Status: {health.status}
              </p>
              <p className="text-gray-400 text-sm mt-1">
                Service: {health.service} v{health.version}
              </p>
            </div>
          )}

          {ollamaHealth && (
            <div className="bg-blue-900/20 border border-blue-800 rounded-lg p-4">
              <p className="text-blue-400">
                ✓ Ollama Status: {ollamaHealth.ollama}
              </p>
            </div>
          )}

          <div className="bg-dark-800 border border-dark-700 rounded-lg p-4">
            <h3 className="text-lg font-semibold mb-2 text-secondary-400">
              Phase 1: Foundation Complete
            </h3>
            <ul className="space-y-1 text-gray-400 text-sm">
              <li>✓ Backend: FastAPI with Ollama integration</li>
              <li>✓ Database: SQLite models configured</li>
              <li>✓ Frontend: React + TypeScript + Vite</li>
              <li>✓ Styling: Tailwind CSS with custom theme</li>
              <li>✓ API: Service layer implemented</li>
            </ul>
          </div>

          <div className="bg-primary-900/20 border border-primary-800 rounded-lg p-4">
            <h3 className="text-lg font-semibold mb-2 text-primary-300">
              Next: Phase 2
            </h3>
            <p className="text-gray-400 text-sm">
              Implementing chat interface with streaming support, conversation management, and model selection.
            </p>
          </div>
        </div>

        <div className="text-center mt-8 text-gray-500 text-sm">
          <p>Built with FastAPI, React, and Ollama</p>
          <p className="mt-1">Mountain/Nature Theme • Dark Mode</p>
        </div>
      </div>
    </div>
  )
}

export default App

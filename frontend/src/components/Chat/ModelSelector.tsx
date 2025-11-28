import { useEffect } from 'react'
import { Cpu, ChevronDown } from 'lucide-react'
import { useChat } from '../../context/ChatContext'

interface ModelSelectorProps {
  selectedModel: string
  onModelChange: (model: string) => void
}

export default function ModelSelector({ selectedModel, onModelChange }: ModelSelectorProps) {
  const { models, loadModels } = useChat()

  useEffect(() => {
    loadModels()
  }, [loadModels])

  const formatModelSize = (size: number): string => {
    const gb = size / (1024 * 1024 * 1024)
    return `${gb.toFixed(1)} GB`
  }

  const currentModel = models.find(m => m.name === selectedModel)

  return (
    <div className="relative">
      <div className="glass rounded-lg glow p-3">
        <div className="flex items-center gap-2 mb-2">
          <Cpu size={16} className="text-primary-400" />
          <span className="text-xs text-gray-400">Active Model</span>
        </div>

        <div className="relative">
          <select
            value={selectedModel}
            onChange={(e) => onModelChange(e.target.value)}
            className="w-full bg-black/50 border border-primary-700/30 rounded px-3 py-2 text-sm text-gray-200 cursor-pointer outline-none focus:border-primary-500 transition-colors"
          >
            {models.length === 0 ? (
              <option value="" className="bg-black">Loading models...</option>
            ) : (
              models.map((model) => (
                <option key={model.name} value={model.name} className="bg-black">
                  {model.name}
                </option>
              ))
            )}
          </select>
        </div>

        {currentModel && (
          <div className="mt-2 flex items-center justify-between text-xs">
            <span className="text-primary-400/60">{formatModelSize(currentModel.size)}</span>
            <span className="text-gray-500">{models.length} available</span>
          </div>
        )}
      </div>
    </div>
  )
}

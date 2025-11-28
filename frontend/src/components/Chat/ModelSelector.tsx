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

  return (
    <div className="relative">
      <div className="flex items-center gap-3 p-3 glass rounded-lg glow">
        <Cpu size={18} className="text-primary-400" />
        <select
          value={selectedModel}
          onChange={(e) => onModelChange(e.target.value)}
          className="bg-transparent flex-1 outline-none text-gray-200 cursor-pointer appearance-none text-sm font-medium"
        >
          {models.length === 0 ? (
            <option value="" className="bg-dark-900">Loading models...</option>
          ) : (
            models.map((model) => (
              <option key={model.name} value={model.name} className="bg-dark-900">
                {model.name} ({formatModelSize(model.size)})
              </option>
            ))
          )}
        </select>
        <ChevronDown size={14} className="text-primary-400/60" />
      </div>

      {models.length > 0 && (
        <div className="mt-2 text-xs text-primary-400/60">
          {models.length} model{models.length !== 1 ? 's' : ''} available
        </div>
      )}
    </div>
  )
}

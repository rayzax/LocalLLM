import { useState, useEffect } from 'react'
import { Upload, File, Trash2, FileText, RefreshCw, Database } from 'lucide-react'
import { api } from '../../services/api'

interface FileInfo {
  id: number
  filename: string
  file_type: string
  file_size: number
  chunks_count: number
  uploaded_at: string
}

export default function DocumentsPanel() {
  const [files, setFiles] = useState<FileInfo[]>([])
  const [uploading, setUploading] = useState(false)
  const [dragActive, setDragActive] = useState(false)
  const [stats, setStats] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  const loadFiles = async () => {
    try {
      const data = await api.getFiles()
      setFiles(data)
    } catch (error) {
      console.error('Error loading files:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadStats = async () => {
    try {
      const data = await api.getRagStats()
      setStats(data)
    } catch (error) {
      console.error('Error loading stats:', error)
    }
  }

  useEffect(() => {
    loadFiles()
    loadStats()
  }, [])

  const handleFileUpload = async (file: File) => {
    setUploading(true)
    try {
      await api.uploadFile(file)
      await loadFiles()
      await loadStats()
    } catch (error) {
      console.error('Error uploading file:', error)
      alert('Failed to upload file: ' + (error as Error).message)
    } finally {
      setUploading(false)
    }
  }

  const handleDelete = async (fileId: number) => {
    if (!confirm('Are you sure you want to delete this file and its embeddings?')) {
      return
    }

    try {
      await api.deleteFile(fileId)
      await loadFiles()
      await loadStats()
    } catch (error) {
      console.error('Error deleting file:', error)
      alert('Failed to delete file')
    }
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setDragActive(true)
  }

  const handleDragLeave = () => {
    setDragActive(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setDragActive(false)

    const file = e.dataTransfer.files[0]
    if (file) {
      handleFileUpload(file)
    }
  }

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      handleFileUpload(file)
    }
  }

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleString()
  }

  return (
    <div className="flex flex-col h-screen bg-black">
      {/* Header */}
      <div className="flex-shrink-0 glass border-b border-primary-700/20 p-4">
        <div className="max-w-5xl mx-auto">
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <Database size={20} className="text-primary-400" />
                <h2 className="text-lg font-semibold text-gray-200">Document Library</h2>
              </div>
              <p className="text-sm text-gray-400">Upload and manage documents for RAG</p>
            </div>
            <button
              onClick={() => { loadFiles(); loadStats(); }}
              className="glass px-4 py-2 rounded-lg text-sm text-gray-200 hover:glow transition-all flex items-center gap-2"
            >
              <RefreshCw size={16} />
              Refresh
            </button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-5xl mx-auto p-6 space-y-6">
          {/* Stats Cards */}
          {stats && (
            <div className="grid grid-cols-3 gap-4">
              <div className="glass p-4 rounded-lg">
                <div className="text-sm text-gray-400 mb-1">Total Files</div>
                <div className="text-2xl font-semibold text-primary-400">{stats.files.total}</div>
              </div>
              <div className="glass p-4 rounded-lg">
                <div className="text-sm text-gray-400 mb-1">Indexed</div>
                <div className="text-2xl font-semibold text-secondary-400">{stats.files.indexed}</div>
              </div>
              <div className="glass p-4 rounded-lg">
                <div className="text-sm text-gray-400 mb-1">Total Chunks</div>
                <div className="text-2xl font-semibold text-cosmic-400">{stats.vector_store.total_chunks}</div>
              </div>
            </div>
          )}

          {/* Upload Area */}
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            className={`glass rounded-lg p-8 text-center transition-all ${
              dragActive ? 'border-primary-500 bg-primary-500/10 glow' : 'border-primary-700/30'
            } ${uploading ? 'opacity-50 pointer-events-none' : ''}`}
          >
            <Upload size={48} className="mx-auto mb-4 text-primary-400" />
            <h3 className="text-lg font-semibold text-gray-200 mb-2">
              {uploading ? 'Uploading...' : 'Upload Document'}
            </h3>
            <p className="text-sm text-gray-400 mb-4">
              Drag and drop or click to select a file
            </p>
            <input
              type="file"
              id="file-upload"
              className="hidden"
              onChange={handleFileInput}
              disabled={uploading}
            />
            <label
              htmlFor="file-upload"
              className="inline-block btn-primary cursor-pointer"
            >
              Choose File
            </label>
            {stats && (
              <p className="text-xs text-gray-500 mt-4">
                Supported: {stats.supported_formats.slice(0, 10).join(', ')}...
              </p>
            )}
          </div>

          {/* Files List */}
          <div className="space-y-3">
            <h3 className="text-md font-semibold text-gray-300 flex items-center gap-2">
              <FileText size={18} className="text-primary-400" />
              Uploaded Documents ({files.length})
            </h3>

            {loading ? (
              <div className="glass p-8 rounded-lg text-center">
                <RefreshCw size={24} className="mx-auto mb-2 text-primary-400 animate-spin" />
                <p className="text-sm text-gray-400">Loading documents...</p>
              </div>
            ) : files.length === 0 ? (
              <div className="glass p-8 rounded-lg text-center">
                <File size={48} className="mx-auto mb-2 text-gray-600" />
                <p className="text-sm text-gray-400">No documents uploaded yet</p>
              </div>
            ) : (
              files.map((file) => (
                <div
                  key={file.id}
                  className="glass p-4 rounded-lg hover:glow transition-all"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3 flex-1 min-w-0">
                      <div className="flex-shrink-0 w-10 h-10 rounded-lg bg-gradient-to-br from-primary-600 to-primary-800 flex items-center justify-center">
                        <FileText size={20} className="text-white" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <h4 className="text-sm font-medium text-gray-200 truncate">
                          {file.filename}
                        </h4>
                        <div className="flex items-center gap-3 text-xs text-gray-400 mt-1">
                          <span>{formatFileSize(file.file_size)}</span>
                          <span>•</span>
                          <span>{file.chunks_count} chunks</span>
                          <span>•</span>
                          <span>{formatDate(file.uploaded_at)}</span>
                        </div>
                      </div>
                    </div>
                    <button
                      onClick={() => handleDelete(file.id)}
                      className="flex-shrink-0 p-2 rounded-lg hover:bg-red-500/20 text-gray-400 hover:text-red-400 transition-colors"
                    >
                      <Trash2 size={18} />
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

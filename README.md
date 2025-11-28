# LLMLocal - Local LLM Dashboard

A comprehensive web-based dashboard for interacting with local LLM models running on Ollama. Built with production-ready architecture for power users who want complete control over their AI workflows.

## Features

### Phase 1: Foundation ✅ (Current)
- FastAPI backend with async support
- React + TypeScript + Vite frontend
- Tailwind CSS with custom mountain/nature theme
- SQLite database for conversations and metadata
- Ollama integration with health checks
- Docker Compose deployment
- Structured logging

### Phase 2: Core Chat (Next)
- Terminal-inspired chat interface
- Streaming responses (Server-Sent Events)
- Conversation management (create, delete, search, tag)
- Model selection and parameter tuning (temperature, top_p, max_tokens)
- Message history persistence
- Export conversations (Markdown, JSON)
- Keyboard shortcuts
- Resource monitoring widget

### Phase 3: RAG System (Planned)
- Full filesystem indexing with ChromaDB
- Real-time file monitoring with Watchdog
- Multi-format file parsing (code, docs, PDFs, etc.)
- Semantic search with hybrid retrieval
- Gitignore-aware scanning
- Configurable exclusion patterns
- Background indexing workers

### Phase 4: Internet Research (Planned)
- DuckDuckGo search integration
- Web scraping with BeautifulSoup4/Playwright
- Multi-step research workflows
- Source tracking and citations
- Research report generation

### Phase 5: Advanced Features (Planned)
- Threat intelligence assistant (CVE lookup, MITRE ATT&CK)
- Code analysis suite with syntax highlighting
- Multi-agent orchestration
- Smart summarization (YouTube, ArXiv, RSS)
- Screenshot analysis with OCR
- Homelab integration (Proxmox, Docker APIs)
- Prompt library with versioning

## Technology Stack

### Backend
- **Framework**: FastAPI with async support
- **LLM**: Ollama Python client
- **Vector DB**: ChromaDB for embeddings
- **Database**: SQLite with SQLAlchemy
- **Monitoring**: Watchdog for file changes
- **Web**: BeautifulSoup4 and Playwright
- **Logging**: Structured JSON logs with structlog

### Frontend
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **HTTP Client**: Axios
- **Icons**: Lucide React
- **Markdown**: react-markdown with syntax highlighting

### DevOps
- Docker Compose for orchestration
- NGINX for frontend serving
- Health check endpoints
- Volume persistence

## Prerequisites

### Required
- **Python**: 3.11 or higher
- **Node.js**: 20 or higher
- **Docker**: 24.0 or higher
- **Docker Compose**: 2.0 or higher
- **Ollama**: Latest version

### Optional
- **GPU**: AMD RX 6650 XT with ROCm support (or NVIDIA with CUDA)
- **RAM**: 16GB+ recommended for larger models
- **Storage**: 50GB+ for models and embeddings

## Installation

### Quick Start with Docker Compose (Recommended)

1. **Clone the repository**
```bash
git clone <repository-url>
cd LLMLocal
```

2. **Create environment file**
```bash
cp backend/.env.example backend/.env
# Edit backend/.env with your preferences
```

3. **Start all services**
```bash
docker-compose up -d
```

4. **Pull your desired Ollama model**
```bash
docker exec -it llmlocal-ollama ollama pull llama3.2:3b
```

5. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Ollama: http://localhost:11434

### Local Development Setup

#### Backend Setup

1. **Navigate to backend directory**
```bash
cd backend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Create .env file**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Run the backend**
```bash
python -m app.main
# Or with uvicorn directly:
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup

1. **Navigate to frontend directory**
```bash
cd frontend
```

2. **Install dependencies**
```bash
npm install
```

3. **Run the development server**
```bash
npm run dev
```

4. **Access frontend**
Open http://localhost:5173 in your browser

## Configuration

### Environment Variables

Key configuration options in `backend/.env`:

```env
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_DEFAULT_MODEL=llama3.2:3b
OLLAMA_EMBEDDING_MODEL=nomic-embed-text

# Database
DATABASE_URL=sqlite:///./llmlocal.db
CHROMADB_PATH=./chromadb_data

# RAG Settings
RAG_CHUNK_SIZE=512
RAG_CHUNK_OVERLAP=50
RAG_MAX_FILE_SIZE_MB=10

# Security
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# Paths
INDEXED_DIRECTORIES=/home/user
EXCLUDED_PATTERNS=node_modules,.git,.cache,__pycache__
```

### Ollama Models

**Recommended models for different use cases:**

- **General Chat**: llama3.2:3b (fast, balanced)
- **Coding**: codellama:7b, deepseek-coder:6.7b
- **Embeddings**: nomic-embed-text
- **Vision**: llava:7b (for screenshot analysis)

**Pull a model:**
```bash
ollama pull llama3.2:3b
ollama pull nomic-embed-text
```

**List installed models:**
```bash
ollama list
```

## API Documentation

Once the backend is running, visit:
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Project Structure

```
LLMLocal/
├── backend/
│   ├── app/
│   │   ├── api/              # API endpoints
│   │   ├── services/         # Business logic
│   │   ├── rag/             # RAG system
│   │   ├── agents/          # Multi-agent system
│   │   ├── integrations/    # External APIs
│   │   └── utils/           # Utilities
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── services/        # API client
│   │   ├── types/           # TypeScript types
│   │   └── styles/          # CSS files
│   ├── package.json
│   └── vite.config.ts
├── docker-compose.yml
└── README.md
```

## Usage

### Basic Chat

1. Navigate to the chat interface
2. Select a model from the dropdown
3. Type your message and press Enter or Ctrl+Enter
4. Adjust parameters (temperature, top_p) as needed
5. View streaming responses in real-time

### Conversation Management

- **New Conversation**: Click "New Chat" or press Ctrl+K
- **Delete Conversation**: Click the delete icon in the sidebar
- **Search Conversations**: Use the search bar in the sidebar
- **Export**: Click export button to save as Markdown or JSON

## Troubleshooting

### Ollama Connection Issues

**Problem**: "Ollama is not accessible" error

**Solutions**:
1. Ensure Ollama is running: `systemctl status ollama` (Linux)
2. Check Ollama is listening: `curl http://localhost:11434/api/tags`
3. Verify OLLAMA_BASE_URL in .env matches your setup
4. Check firewall settings

### GPU Not Detected

**For AMD GPUs (ROCm)**:
```bash
# Check ROCm installation
rocm-smi

# Set environment variable
export HSA_OVERRIDE_GFX_VERSION=10.3.0  # For RX 6650 XT
```

**For NVIDIA GPUs (CUDA)**:
```bash
# Check CUDA installation
nvidia-smi

# Ensure docker has GPU access
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

### Port Conflicts

If ports 3000, 8000, or 11434 are in use, modify:
- Frontend port: `docker-compose.yml` → `frontend.ports`
- Backend port: `docker-compose.yml` → `backend.ports`
- Ollama port: `docker-compose.yml` → `ollama.ports`

### Database Errors

**Reset database**:
```bash
rm backend/llmlocal.db
# Backend will recreate on next start
```

## Development

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests (when implemented)
cd frontend
npm test
```

### Code Quality

```bash
# Backend linting
cd backend
ruff check .

# Frontend linting
cd frontend
npm run lint
```

### Building for Production

```bash
# Build all services
docker-compose build

# Build specific service
docker-compose build backend
docker-compose build frontend
```

## Performance Optimization

### For Low-End Hardware

1. Use smaller models (1B-3B parameters)
2. Reduce context window (max_tokens)
3. Disable background indexing
4. Limit concurrent requests

### For High-End Hardware

1. Use larger models (7B-13B parameters)
2. Enable GPU acceleration
3. Increase chunk size for RAG
4. Enable aggressive caching

## Security Considerations

- **Local Only**: By default, services bind to localhost
- **No Authentication**: Phase 1 has no auth (add JWT in production)
- **File Access**: RAG system can read user files (configure exclusions)
- **API Keys**: Never commit .env files to version control
- **Docker**: Run containers as non-root user in production

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style

- **Python**: Follow PEP 8, use type hints
- **TypeScript**: Enable strict mode, use proper typing
- **Commits**: Use conventional commits (feat:, fix:, docs:, etc.)

## Roadmap

- [x] Phase 1: Foundation (Backend, Frontend, Docker)
- [ ] Phase 2: Core Chat Interface
- [ ] Phase 3: RAG System
- [ ] Phase 4: Internet Research
- [ ] Phase 5: Advanced Features
- [ ] Phase 6: Polish & Testing

## License

MIT License - see LICENSE file for details

## Acknowledgments

- **Ollama** - Local LLM runtime
- **FastAPI** - Modern Python web framework
- **React** - UI library
- **Tailwind CSS** - Utility-first CSS framework
- **ChromaDB** - Vector database for embeddings

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing documentation
- Review troubleshooting section

---

**Built with ❤️ for power users who want complete control over their AI workflows**

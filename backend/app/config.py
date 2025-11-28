"""
Configuration management for LLMLocal application.
Uses pydantic-settings for environment variable validation.
"""
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Server Configuration
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    reload: bool = Field(default=True, description="Auto-reload on code changes")

    # Ollama Configuration
    ollama_base_url: str = Field(default="http://localhost:11434", description="Ollama API base URL")
    ollama_default_model: str = Field(default="llama3.2:3b", description="Default LLM model")
    ollama_embedding_model: str = Field(default="nomic-embed-text", description="Embedding model")

    # Database
    database_url: str = Field(default="sqlite:///./llmlocal.db", description="SQLite database URL")
    chromadb_path: str = Field(default="./chromadb_data", description="ChromaDB storage path")

    # RAG Settings
    rag_chunk_size: int = Field(default=512, description="Text chunk size for embeddings")
    rag_chunk_overlap: int = Field(default=50, description="Overlap between chunks")
    rag_max_file_size_mb: int = Field(default=10, description="Maximum file size to index (MB)")
    rag_top_k_results: int = Field(default=5, description="Number of top results to return")

    # Web Search
    duckduckgo_enabled: bool = Field(default=True, description="Enable DuckDuckGo search")
    searxng_url: str = Field(default="", description="Optional SearxNG instance URL")
    max_search_results: int = Field(default=10, description="Maximum search results")

    # Security
    secret_key: str = Field(default="your-secret-key-change-this", description="JWT secret key")
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(default=30, description="Token expiration time")
    allowed_origins: str = Field(
        default="http://localhost:5173,http://localhost:3000",
        description="CORS allowed origins (comma-separated)"
    )

    # Paths
    indexed_directories: str = Field(default="/home/user", description="Directories to index")
    excluded_patterns: str = Field(
        default="node_modules,.git,.cache,__pycache__,venv,.venv,dist,build",
        description="Patterns to exclude from indexing"
    )
    sensitive_patterns: str = Field(
        default=".ssh,.gnupg,.password-store,.aws,.docker,*.key,*.pem",
        description="Sensitive paths to always exclude"
    )

    # API Keys (Optional)
    nvd_api_key: str = Field(default="", description="NVD API key")
    alienvault_api_key: str = Field(default="", description="AlienVault OTX API key")
    proxmox_host: str = Field(default="", description="Proxmox host")
    proxmox_user: str = Field(default="", description="Proxmox username")
    proxmox_password: str = Field(default="", description="Proxmox password")

    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(default="json", description="Log format (json or text)")

    # Background Tasks
    celery_broker_url: str = Field(default="redis://localhost:6379/0", description="Celery broker URL")
    celery_result_backend: str = Field(default="redis://localhost:6379/0", description="Celery result backend")

    # Rate Limiting
    rate_limit_per_minute: int = Field(default=60, description="API rate limit per minute")

    # File Upload
    max_upload_size_mb: int = Field(default=50, description="Maximum upload size (MB)")

    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse allowed origins from comma-separated string."""
        return [origin.strip() for origin in self.allowed_origins.split(",")]

    @property
    def indexed_directories_list(self) -> List[str]:
        """Parse indexed directories from comma-separated string."""
        return [path.strip() for path in self.indexed_directories.split(",")]

    @property
    def excluded_patterns_list(self) -> List[str]:
        """Parse excluded patterns from comma-separated string."""
        return [pattern.strip() for pattern in self.excluded_patterns.split(",")]

    @property
    def sensitive_patterns_list(self) -> List[str]:
        """Parse sensitive patterns from comma-separated string."""
        return [pattern.strip() for pattern in self.sensitive_patterns.split(",")]


# Global settings instance
settings = Settings()

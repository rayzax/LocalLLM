/**
 * TypeScript type definitions for LLMLocal
 */

export interface Message {
  id: number;
  role: 'user' | 'assistant' | 'system';
  content: string;
  created_at: string;
  token_count: number;
}

export interface Conversation {
  id: number;
  title: string;
  model: string;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export interface Model {
  name: string;
  modified_at: string;
  size: number;
  digest: string;
  details?: {
    format: string;
    family: string;
    families: string[];
    parameter_size: string;
    quantization_level: string;
  };
}

export interface ChatRequest {
  conversation_id?: number;
  message: string;
  model?: string;
  temperature?: number;
  top_p?: number;
  max_tokens?: number;
  stream?: boolean;
  system_prompt?: string;
}

export interface ChatResponse {
  conversation_id: number;
  message: string;
  model: string;
}

export interface Settings {
  ollama_base_url: string;
  ollama_default_model: string;
  ollama_embedding_model: string;
  rag_chunk_size: number;
  rag_chunk_overlap: number;
  rag_max_file_size_mb: number;
  rag_top_k_results: number;
  indexed_directories: string[];
  excluded_patterns: string[];
  duckduckgo_enabled: boolean;
  max_search_results: number;
}

export interface ApiError {
  detail: string;
  error?: string;
}

export interface HealthStatus {
  status: string;
  service: string;
  version: string;
}

export interface OllamaHealth {
  status: string;
  ollama: string;
}

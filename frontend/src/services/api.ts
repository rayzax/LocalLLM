/**
 * API service for communicating with the backend
 */
import axios, { AxiosInstance, AxiosError } from 'axios';
import type {
  Conversation,
  Message,
  Model,
  ChatRequest,
  ChatResponse,
  Settings,
  HealthStatus,
  OllamaHealth,
  ApiError
} from '../types';

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: '/api',
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 30000,
    });

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError<ApiError>) => {
        const message = error.response?.data?.detail || error.message || 'An error occurred';
        console.error('API Error:', message);
        return Promise.reject(new Error(message));
      }
    );
  }

  // Health endpoints
  async checkHealth(): Promise<HealthStatus> {
    const response = await this.client.get<HealthStatus>('/health');
    return response.data;
  }

  async checkOllamaHealth(): Promise<OllamaHealth> {
    const response = await this.client.get<OllamaHealth>('/chat/health');
    return response.data;
  }

  // Model endpoints
  async getModels(): Promise<Model[]> {
    const response = await this.client.get<{ models: Model[] }>('/chat/models');
    return response.data.models;
  }

  // Conversation endpoints
  async getConversations(skip = 0, limit = 50): Promise<Conversation[]> {
    const response = await this.client.get<{ conversations: Conversation[] }>(
      '/chat/conversations',
      { params: { skip, limit } }
    );
    return response.data.conversations;
  }

  async createConversation(
    title: string,
    model: string,
    system_prompt?: string
  ): Promise<Conversation> {
    const response = await this.client.post<Conversation>('/chat/conversations', {
      title,
      model,
      system_prompt,
    });
    return response.data;
  }

  async deleteConversation(conversationId: number): Promise<void> {
    await this.client.delete(`/chat/conversations/${conversationId}`);
  }

  // Message endpoints
  async getMessages(conversationId: number): Promise<Message[]> {
    const response = await this.client.get<{ messages: Message[] }>(
      `/chat/conversations/${conversationId}/messages`
    );
    return response.data.messages;
  }

  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    const response = await this.client.post<ChatResponse>('/chat/chat', request);
    return response.data;
  }

  async sendMessageStream(
    request: ChatRequest,
    onChunk: (chunk: string) => void,
    onComplete: () => void,
    onError: (error: Error) => void
  ): Promise<void> {
    try {
      const response = await fetch('/api/chat/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ ...request, stream: true }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to send message');
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('No response body');
      }

      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        onChunk(chunk);
      }

      onComplete();
    } catch (error) {
      onError(error instanceof Error ? error : new Error('Unknown error'));
    }
  }

  // Settings endpoints
  async getSettings(): Promise<Settings> {
    const response = await this.client.get<{ settings: Settings }>('/settings');
    return response.data.settings;
  }

  async getSetting(key: string): Promise<any> {
    const response = await this.client.get(`/settings/${key}`);
    return response.data;
  }

  async updateSetting(key: string, value: any, description?: string): Promise<void> {
    await this.client.post('/settings', { key, value, description });
  }

  async deleteSetting(key: string): Promise<void> {
    await this.client.delete(`/settings/${key}`);
  }
}

export const api = new ApiService();
export default api;

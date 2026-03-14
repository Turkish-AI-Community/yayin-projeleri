import axios from 'axios';
import axiosRetry from 'axios-retry';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Retry logic for failing requests (e.g. timeout on indexing)
axiosRetry(api, {
  retries: 3,
  retryDelay: axiosRetry.exponentialDelay,
  retryCondition: (error) => {
    return axiosRetry.isNetworkOrIdempotentRequestError(error) || error.response?.status === 429;
  },
});

export interface QueryResponse {
  answer: string;
  sources?: string[];
  [key: string]: unknown;
}

export interface EmbedResponse {
  message: string;
}

export const ragService = {
  embedDocuments: async (): Promise<EmbedResponse> => {
    const { data } = await api.post<EmbedResponse>('/embed');
    return data;
  },

  query: async (question: string): Promise<QueryResponse> => {
    const { data } = await api.post<QueryResponse>('/query', { question });
    return data;
  },

  uploadFile: async (file: File): Promise<{ message: string; file_path: string }> => {
    const formData = new FormData();
    formData.append('file', file);
    const { data } = await api.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return data;
  },

  getEmbeddingStatus: async (): Promise<{ embedding_in_progress: boolean }> => {
    const { data } = await api.get('/status');
    return data;
  },
};

export default api;

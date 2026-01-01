import axios, { AxiosError } from 'axios';
import type { ChatRequest, ChatResponse, StatusResponse, ApiError } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds timeout
});

// Error handler
const handleApiError = (error: AxiosError<ApiError>): never => {
  if (error.response) {
    // Server responded with error
    throw new Error(error.response.data.detail || 'An error occurred');
  } else if (error.request) {
    // Request made but no response
    throw new Error('No response from server. Please check if the backend is running.');
  } else {
    // Error setting up request
    throw new Error(error.message || 'An unexpected error occurred');
  }
};

export const api = {
  /**
   * Get API status and index information
   */
  async getStatus(): Promise<StatusResponse> {
    try {
      const response = await apiClient.get<StatusResponse>('/');
      return response.data;
    } catch (error) {
      return handleApiError(error as AxiosError<ApiError>);
    }
  },

  /**
   * Send a chat message and get response
   */
  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    try {
      const response = await apiClient.post<ChatResponse>('/chat', request);
      return response.data;
    } catch (error) {
      return handleApiError(error as AxiosError<ApiError>);
    }
  },

  /**
   * Clear conversation history
   */
  async clearHistory(): Promise<void> {
    try {
      await apiClient.post('/clear');
    } catch (error) {
      return handleApiError(error as AxiosError<ApiError>);
    }
  },

  /**
   * Health check
   */
  async healthCheck(): Promise<{ status: string }> {
    try {
      const response = await apiClient.get<{ status: string }>('/health');
      return response.data;
    } catch (error) {
      return handleApiError(error as AxiosError<ApiError>);
    }
  },
};

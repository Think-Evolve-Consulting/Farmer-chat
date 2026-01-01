export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export interface ChatRequest {
  message: string;
  include_context?: boolean;
}

export interface ChatResponse {
  response: string;
  has_context: boolean;
}

export interface StatusResponse {
  status: string;
  index_loaded: boolean;
  total_chunks?: number;
}

export interface ApiError {
  detail: string;
}

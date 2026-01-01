import React, { useState, useEffect, useRef } from 'react';
import { api } from '../services/api';
import { ChatMessage } from './ChatMessage';
import { ChatInput } from './ChatInput';
import type { ChatMessage as ChatMessageType, StatusResponse } from '../types';

export const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessageType[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [status, setStatus] = useState<StatusResponse | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Load status on mount
  useEffect(() => {
    const loadStatus = async () => {
      try {
        const statusData = await api.getStatus();
        setStatus(statusData);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load status');
      }
    };
    loadStatus();
  }, []);

  const handleSendMessage = async (messageText: string) => {
    // Add user message to chat
    const userMessage: ChatMessageType = {
      role: 'user',
      content: messageText,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);
    setError(null);

    try {
      // Send to API
      const response = await api.sendMessage({
        message: messageText,
        include_context: true,
      });

      // Add assistant response to chat
      const assistantMessage: ChatMessageType = {
        role: 'assistant',
        content: response.response,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send message');
    } finally {
      setLoading(false);
    }
  };

  const handleClearHistory = async () => {
    if (window.confirm('Are you sure you want to clear the conversation?')) {
      try {
        await api.clearHistory();
        setMessages([]);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to clear history');
      }
    }
  };

  return (
    <div className="chat-container">
      {/* Header */}
      <div className="chat-header">
        <div className="header-content">
          <h1>Farmer Chat Assistant</h1>
          {status && (
            <div className="status-info">
              <span className={`status-indicator ${status.index_loaded ? 'loaded' : 'not-loaded'}`}>
                {status.index_loaded ? '●' : '○'}
              </span>
              <span className="status-text">
                {status.index_loaded
                  ? `${status.total_chunks?.toLocaleString()} chunks indexed`
                  : 'No index loaded'}
              </span>
            </div>
          )}
        </div>
        <button className="clear-button" onClick={handleClearHistory}>
          Clear Chat
        </button>
      </div>

      {/* Error display */}
      {error && (
        <div className="error-banner">
          <span className="error-icon">⚠️</span>
          <span>{error}</span>
          <button className="error-close" onClick={() => setError(null)}>
            ×
          </button>
        </div>
      )}

      {/* Messages */}
      <div className="messages-container">
        {messages.length === 0 ? (
          <div className="welcome-message">
            <h2>Welcome to Farmer Chat!</h2>
            <p>Ask me anything about farming practices, crop management, or agricultural advice.</p>
            <div className="example-questions">
              <p>Try asking:</p>
              <ul>
                <li>"What is crop rotation?"</li>
                <li>"How much sulphate should I use?"</li>
                <li>"What are the best practices for pest management?"</li>
              </ul>
            </div>
          </div>
        ) : (
          messages.map((msg, idx) => <ChatMessage key={idx} message={msg} />)
        )}
        {loading && (
          <div className="loading-indicator">
            <span className="loading-dot">●</span>
            <span className="loading-dot">●</span>
            <span className="loading-dot">●</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <ChatInput
        onSendMessage={handleSendMessage}
        disabled={loading}
        placeholder="Ask about farming practices, crops, or agricultural advice..."
      />
    </div>
  );
};

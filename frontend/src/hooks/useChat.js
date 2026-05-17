import { useState, useRef, useCallback } from 'react';
import { sendChat, clearChatHistory } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

export function useChat() {
  const [messages, setMessages] = useState([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState(null);
  const abortRef = useRef(null);
  const { getAccessToken } = useAuth();

  const sendMessage = useCallback(
    async (text) => {
      if (!text.trim() || isStreaming) return;
      setError(null);

      const userMsg = {
        id: crypto.randomUUID(),
        role: 'user',
        content: text.trim(),
        displayText: text.trim(),
      };

      const assistantMsg = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: '',
        products: [],
      };

      setMessages((prev) => [...prev, userMsg, assistantMsg]);
      setIsStreaming(true);
      abortRef.current = new AbortController();

      try {
        const accessToken = await getAccessToken();
        const response = await sendChat({
          message: text.trim(),
          signal: abortRef.current.signal,
          accessToken,
        });

        const responseText = response.response || response;
        const products = response.products || [];

        setMessages((prev) => {
          const copy = [...prev];
          const last = copy[copy.length - 1];
          copy[copy.length - 1] = {
            ...last,
            content: responseText,
            products,
          };
          return copy;
        });
      } catch (err) {
        if (err.name === 'AbortError') {
          return;
        }
        setError(err.message || 'Unknown error');
        setMessages((prev) => {
          const last = prev[prev.length - 1];
          return last?.content === '' ? prev.slice(0, -1) : prev;
        });
      } finally {
        setIsStreaming(false);
      }
    },
    [getAccessToken, isStreaming]
  );

  const clearChat = useCallback(() => {
    abortRef.current?.abort();
    setMessages([]);
    setError(null);
    setIsStreaming(false);

    void (async () => {
      try {
        const accessToken = await getAccessToken();
        await clearChatHistory({ accessToken });
      } catch (err) {
        console.error('Failed to clear backend chat history:', err);
      }
    })();
  }, [getAccessToken]);

  const stopStreaming = useCallback(() => {
    abortRef.current?.abort();
  }, []);

  return { messages, isStreaming, error, sendMessage, clearChat, stopStreaming };
}

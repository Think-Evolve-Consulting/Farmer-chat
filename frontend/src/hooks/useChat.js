import { useState, useRef, useCallback } from 'react';
import { streamChat } from '../services/api';

/**
 * Converts a File object to a base64 data URL.
 */
function fileToBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = () => reject(new Error('Failed to read file'));
    reader.readAsDataURL(file);
  });
}

/**
 * Core chat hook. Manages messages, streaming, and image uploads.
 *
 * @param {string} language - Currently selected language code
 * @returns {{
 *   messages: Array,
 *   isStreaming: boolean,
 *   error: string|null,
 *   sendMessage: Function,
 *   clearChat: Function,
 * }}
 */
export function useChat(language) {
  const [messages, setMessages] = useState([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState(null);
  const abortRef = useRef(null);

  const sendMessage = useCallback(async (text, imageFile = null) => {
    if ((!text.trim() && !imageFile) || isStreaming) return;
    setError(null);

    // --- Build user message content ---
    let userApiContent;
    let imagePreviewUrl = null;

    if (imageFile) {
      const base64 = await fileToBase64(imageFile);
      imagePreviewUrl = URL.createObjectURL(imageFile);
      // Vision-compatible content array (Azure OpenAI / OpenAI format)
      userApiContent = [
        { type: 'image_url', image_url: { url: base64, detail: 'auto' } },
        { type: 'text', text: text.trim() || 'Please analyze this crop image.' },
      ];
    } else {
      userApiContent = text.trim();
    }

    const userMsg = {
      id: Date.now(),
      role: 'user',
      content: userApiContent,        // sent to API
      displayText: text.trim(),       // shown in UI
      imagePreview: imagePreviewUrl,  // blob URL for preview
    };

    // Placeholder for the streaming assistant reply
    const assistantMsg = {
      id: Date.now() + 1,
      role: 'assistant',
      content: '',
    };

    setMessages(prev => [...prev, userMsg, assistantMsg]);
    setIsStreaming(true);

    // Build history to send to API (all past messages + the new user one)
    // We snapshot before state update so we get the right history
    const apiHistory = [...messages, userMsg].map(m => ({
      role: m.role,
      content: m.content,
    }));

    abortRef.current = new AbortController();

    try {
      for await (const item of streamChat({
        messages: apiHistory,
        language,
        signal: abortRef.current.signal,
      })) {
        if (item.type === 'text') {
          const cleaned = item.content.replace(/\[doc\d+\]/gi, '');
          setMessages(prev => {
            const copy = [...prev];
            const last = copy[copy.length - 1];
            copy[copy.length - 1] = { ...last, content: last.content + cleaned };
            return copy;
          });
        } else if (item.type === 'citations') {
          setMessages(prev => {
            const copy = [...prev];
            const last = copy[copy.length - 1];
            copy[copy.length - 1] = { ...last, citations: item.data };
            return copy;
          });
        }
      }
    } catch (err) {
      if (err.name === 'AbortError') {
        // User cancelled — keep whatever was streamed so far
        return;
      }
      setError(err.message || 'Unknown error');
      // Remove the empty assistant placeholder on hard errors
      setMessages(prev => {
        const last = prev[prev.length - 1];
        return last?.content === '' ? prev.slice(0, -1) : prev;
      });
    } finally {
      setIsStreaming(false);
    }
  }, [messages, language, isStreaming]);

  const clearChat = useCallback(() => {
    abortRef.current?.abort();
    setMessages([]);
    setError(null);
    setIsStreaming(false);
  }, []);

  const stopStreaming = useCallback(() => {
    abortRef.current?.abort();
  }, []);

  return { messages, isStreaming, error, sendMessage, clearChat, stopStreaming };
}

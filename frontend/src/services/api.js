/**
 * Kisan API Service - connects to FastAPI backend
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

function buildApiUrl(path) {
  const base = API_BASE_URL.endsWith('/') ? API_BASE_URL.slice(0, -1) : API_BASE_URL;
  const nextPath = path.startsWith('/') ? path : `/${path}`;
  return `${base}${nextPath}`;
}

function buildHeaders(accessToken) {
  const headers = { 'Content-Type': 'application/json' };
  if (accessToken) {
    headers.Authorization = `Bearer ${accessToken}`;
  }
  return headers;
}

export async function sendChat({ message, signal, accessToken }) {
  try {
    const response = await fetch(buildApiUrl('/chat'), {
      method: 'POST',
      headers: buildHeaders(accessToken),
      body: JSON.stringify({ message, include_context: true }),
      signal,
    });

    if (!response.ok) {
      const errBody = await response.json().catch(() => ({}));
      throw new Error(errBody.detail || `API error ${response.status}`);
    }

    const data = await response.json();
    return {
      response: data.response,
      products: data.products || [],
      context: data.context_results || [],
    };
  } catch (err) {
    if (err.name === 'AbortError') throw err;
    throw new Error(`Network error: ${err.message}`);
  }
}

export async function clearChatHistory({ accessToken } = {}) {
  try {
    const response = await fetch(buildApiUrl('/clear'), {
      method: 'POST',
      headers: buildHeaders(accessToken),
    });

    if (!response.ok) {
      const errBody = await response.json().catch(() => ({}));
      throw new Error(errBody.detail || `API error ${response.status}`);
    }

    return response.json().catch(() => ({}));
  } catch (err) {
    throw new Error(`Network error: ${err.message}`);
  }
}

import { useState, useRef, useCallback } from 'react';

function ImageIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
      <circle cx="8.5" cy="8.5" r="1.5"/>
      <polyline points="21 15 16 10 5 21"/>
    </svg>
  );
}

function SendIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
      <path d="M2 12L22 2 12 22 10 13 2 12z"/>
    </svg>
  );
}

function StopIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
      <rect x="4" y="4" width="16" height="16" rx="2"/>
    </svg>
  );
}

function XIcon() {
  return (
    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
      <line x1="18" y1="6" x2="6" y2="18"/>
      <line x1="6" y1="6" x2="18" y2="18"/>
    </svg>
  );
}

const MAX_FILE_SIZE_MB = 5;
const ACCEPTED_TYPES = ['image/jpeg', 'image/png', 'image/webp', 'image/gif'];

export default function ChatInput({ onSend, onStop, isStreaming, t }) {
  const [text, setText] = useState('');
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [dragOver, setDragOver] = useState(false);
  const [fileError, setFileError] = useState('');
  const textareaRef = useRef(null);
  const fileInputRef = useRef(null);

  const canSend = (text.trim() || imageFile) && !isStreaming;

  const handleImageSelect = useCallback((file) => {
    setFileError('');
    if (!file) return;
    if (!ACCEPTED_TYPES.includes(file.type)) {
      setFileError('Only JPG, PNG, WebP, GIF images are accepted.');
      return;
    }
    if (file.size > MAX_FILE_SIZE_MB * 1024 * 1024) {
      setFileError(`Image must be under ${MAX_FILE_SIZE_MB}MB.`);
      return;
    }
    setImageFile(file);
    setImagePreview(URL.createObjectURL(file));
  }, []);

  const removeImage = useCallback(() => {
    if (imagePreview) URL.revokeObjectURL(imagePreview);
    setImageFile(null);
    setImagePreview(null);
    setFileError('');
    if (fileInputRef.current) fileInputRef.current.value = '';
  }, [imagePreview]);

  const handleSubmit = useCallback(() => {
    if (!canSend) return;
    onSend(text, imageFile);
    setText('');
    removeImage();
    textareaRef.current?.focus();
  }, [canSend, text, imageFile, onSend, removeImage]);

  const handleKeyDown = useCallback((e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  }, [handleSubmit]);

  // Auto-resize textarea
  const handleTextChange = useCallback((e) => {
    setText(e.target.value);
    const el = e.target;
    el.style.height = 'auto';
    el.style.height = Math.min(el.scrollHeight, 120) + 'px';
  }, []);

  // Drag & drop support
  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    setDragOver(true);
  }, []);
  const handleDragLeave = useCallback(() => setDragOver(false), []);
  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files?.[0];
    if (file) handleImageSelect(file);
  }, [handleImageSelect]);

  return (
    <div className="px-4 pb-3 pt-2 border-t border-gray-100 bg-white shrink-0">
      {/* Image preview strip */}
      {imagePreview && (
        <div className="mb-2 flex items-center gap-2 animate-fade-in">
          <div className="relative w-16 h-16 rounded-lg overflow-hidden border border-gray-200 shrink-0">
            <img src={imagePreview} alt="Selected" className="w-full h-full object-cover"/>
            <button
              onClick={removeImage}
              className="absolute top-0.5 right-0.5 w-5 h-5 bg-gray-800 bg-opacity-70 text-white rounded-full flex items-center justify-center hover:bg-opacity-90 transition"
              title={t.removeImage}
            >
              <XIcon />
            </button>
          </div>
          <span className="text-xs text-gray-500 truncate max-w-[160px]">{imageFile?.name}</span>
        </div>
      )}

      {/* File error */}
      {fileError && (
        <p className="text-xs text-red-500 mb-1.5 px-1">{fileError}</p>
      )}

      {/* Input bar */}
      <div
        className={`flex items-end gap-2 bg-gray-100 rounded-2xl px-3 py-2 transition-all ${
          dragOver ? 'ring-2 ring-primary-400 bg-primary-50' : 'focus-within:ring-2 focus-within:ring-primary-300'
        }`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        {/* Image upload button */}
        <button
          type="button"
          onClick={() => fileInputRef.current?.click()}
          className="text-gray-400 hover:text-primary-600 transition-colors shrink-0 pb-0.5"
          title={t.attachImage}
          aria-label={t.attachImage}
        >
          <ImageIcon />
        </button>
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          className="hidden"
          onChange={(e) => handleImageSelect(e.target.files?.[0])}
        />

        {/* Text input */}
        <textarea
          ref={textareaRef}
          value={text}
          onChange={handleTextChange}
          onKeyDown={handleKeyDown}
          placeholder={t.inputPlaceholder}
          rows={1}
          className="flex-1 bg-transparent text-gray-800 text-sm placeholder-gray-400 resize-none outline-none leading-relaxed min-h-[24px] max-h-[120px] overflow-y-auto"
          style={{ height: '24px' }}
          disabled={isStreaming}
        />

        {/* Send / Stop button */}
        {isStreaming ? (
          <button
            type="button"
            onClick={onStop}
            className="w-8 h-8 rounded-full bg-red-500 hover:bg-red-600 text-white flex items-center justify-center transition-colors shrink-0"
            title="Stop"
            aria-label="Stop generating"
          >
            <StopIcon />
          </button>
        ) : (
          <button
            type="button"
            onClick={handleSubmit}
            disabled={!canSend}
            className={`w-8 h-8 rounded-full flex items-center justify-center transition-all shrink-0 ${
              canSend
                ? 'bg-primary-700 hover:bg-primary-800 text-white shadow-sm'
                : 'bg-gray-300 text-gray-400 cursor-not-allowed'
            }`}
            title={t.send}
            aria-label={t.send}
          >
            <SendIcon />
          </button>
        )}
      </div>

      {/* Hint */}
      <p className="text-center text-xs text-gray-400 mt-1.5">
        {t.poweredBy}
      </p>
    </div>
  );
}

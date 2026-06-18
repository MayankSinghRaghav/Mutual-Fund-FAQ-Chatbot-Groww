'use client';
import { useState, useEffect, useRef, useCallback } from 'react';

type Role = 'user' | 'assistant';

interface Message {
  role: Role;
  content: string;
  ts: number;
}

const STORAGE_KEY = 'groww-chat-history';

const GREETING: Message = {
  role: 'assistant',
  content: "Hi! I'm your Groww Mutual Fund Assistant. Ask me anything about HDFC schemes!",
  ts: 0,
};

const SUGGESTIONS = [
  'What is the expense ratio of HDFC Flexi Cap Fund?',
  'How do I start a SIP?',
  'Which HDFC funds are good for beginners?',
  'Explain exit load in simple terms',
];

function formatTime(ts: number): string {
  if (!ts) return '';
  return new Date(ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

/**
 * Lightweight, dependency-free renderer for the bot's text.
 * Handles paragraphs, bullet lists, and **bold** spans without
 * using dangerouslySetInnerHTML so untrusted text stays safe.
 */
function renderContent(text: string) {
  const lines = text.split('\n');
  const blocks: React.ReactNode[] = [];
  let listItems: string[] = [];

  const flushList = (key: string) => {
    if (listItems.length === 0) return;
    blocks.push(
      <ul key={key} className="list-disc pl-4 space-y-1 my-1">
        {listItems.map((item, idx) => (
          <li key={idx}>{renderInline(item)}</li>
        ))}
      </ul>
    );
    listItems = [];
  };

  lines.forEach((rawLine, i) => {
    const line = rawLine.trimEnd();
    const bullet = line.match(/^\s*(?:[-•*]|\d+\.)\s+(.*)$/);
    if (bullet) {
      listItems.push(bullet[1]);
      return;
    }
    flushList(`list-${i}`);
    if (line.trim() === '') return;
    blocks.push(
      <p key={`p-${i}`} className="my-0.5">
        {renderInline(line)}
      </p>
    );
  });
  flushList('list-end');

  return blocks.length > 0 ? blocks : text;
}

function renderInline(text: string) {
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  return parts.map((part, i) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      return <strong key={i}>{part.slice(2, -2)}</strong>;
    }
    return <span key={i}>{part}</span>;
  });
}

export default function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([GREETING]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [hasUnread, setHasUnread] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Restore conversation from a previous visit.
  useEffect(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        const parsed = JSON.parse(saved) as Message[];
        // A post-mount read of localStorage keeps SSR markup and the first
        // client render identical, so this setState is intentional.
        // eslint-disable-next-line react-hooks/set-state-in-effect
        if (Array.isArray(parsed) && parsed.length > 0) setMessages(parsed);
      }
    } catch {
      /* ignore malformed storage */
    }
  }, []);

  const openChat = useCallback(() => {
    setIsOpen(true);
    setHasUnread(false);
  }, []);

  // Gently invite the user after the page settles.
  useEffect(() => {
    const timer = setTimeout(() => openChat(), 1200);
    return () => clearTimeout(timer);
  }, [openChat]);

  // Persist and auto-scroll whenever the thread changes.
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(messages));
    } catch {
      /* storage may be unavailable */
    }
    if (scrollRef.current) {
      scrollRef.current.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' });
    }
  }, [messages, isLoading]);

  // Focus the input when the window opens.
  useEffect(() => {
    if (isOpen) {
      const t = setTimeout(() => inputRef.current?.focus(), 150);
      return () => clearTimeout(t);
    }
  }, [isOpen]);

  // Auto-grow the textarea up to a few lines.
  useEffect(() => {
    const el = inputRef.current;
    if (!el) return;
    el.style.height = 'auto';
    el.style.height = `${Math.min(el.scrollHeight, 96)}px`;
  }, [input]);

  const sendMessage = useCallback(
    async (text: string) => {
      const trimmed = text.trim();
      if (!trimmed || isLoading) return;

      setMessages(prev => [...prev, { role: 'user', content: trimmed, ts: Date.now() }]);
      setInput('');
      setIsLoading(true);

      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const res = await fetch(`${apiUrl}/chat`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ query: trimmed }),
        });
        if (!res.ok) throw new Error(`Request failed: ${res.status}`);
        const data = await res.json();
        setMessages(prev => [
          ...prev,
          { role: 'assistant', content: data.answer ?? 'Sorry, I could not find an answer.', ts: Date.now() },
        ]);
      } catch {
        setMessages(prev => [
          ...prev,
          {
            role: 'assistant',
            content: "Sorry, I'm having trouble connecting to the server. Please try again in a moment.",
            ts: Date.now(),
          },
        ]);
      } finally {
        setIsLoading(false);
        if (!isOpen) setHasUnread(true);
        inputRef.current?.focus();
      }
    },
    [isLoading, isOpen]
  );

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage(input);
    }
  };

  const resetChat = () => {
    setMessages([GREETING]);
    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch {
      /* ignore */
    }
    inputRef.current?.focus();
  };

  const showSuggestions = messages.length <= 1 && !isLoading;

  return (
    <>
      {/* Floating Button */}
      {!isOpen && (
        <button
          onClick={openChat}
          aria-label="Open Groww Assistant chat"
          className="fixed bottom-6 right-6 w-14 h-14 bg-[#00d09c] rounded-full shadow-lg flex items-center justify-center text-white text-2xl z-50 hover:scale-110 transition-transform"
        >
          💬
          {hasUnread && (
            <span className="absolute top-0 right-0 w-3.5 h-3.5 bg-red-500 border-2 border-white rounded-full" />
          )}
        </button>
      )}

      {/* Chat Window */}
      {isOpen && (
        <div
          role="dialog"
          aria-label="Groww Mutual Fund Assistant"
          onKeyDown={e => {
            if (e.key === 'Escape') setIsOpen(false);
          }}
          className="fixed bottom-6 right-6 w-[calc(100vw-3rem)] sm:w-96 h-[min(500px,calc(100vh-3rem))] bg-white rounded-2xl shadow-2xl flex flex-col z-50 border border-gray-100 overflow-hidden"
        >
          {/* Header */}
          <div className="bg-[#00d09c] p-4 flex justify-between items-center text-white">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-white rounded-full flex items-center justify-center text-[#00d09c] font-bold">
                G
              </div>
              <div className="flex flex-col leading-tight">
                <span className="font-semibold text-sm">Groww Assistant</span>
                <span className="flex items-center gap-1 text-[11px] text-white/80">
                  <span className="w-1.5 h-1.5 bg-white rounded-full" />
                  Online
                </span>
              </div>
            </div>
            <div className="flex items-center gap-1">
              <button
                onClick={resetChat}
                aria-label="Start a new chat"
                title="New chat"
                className="hover:opacity-70 text-sm px-2 py-1 rounded"
              >
                ↻
              </button>
              <button
                onClick={() => setIsOpen(false)}
                aria-label="Close chat"
                className="hover:opacity-70 text-lg px-1"
              >
                ✕
              </button>
            </div>
          </div>

          {/* Messages */}
          <div
            ref={scrollRef}
            role="log"
            aria-live="polite"
            aria-atomic="false"
            className="flex-1 p-4 overflow-y-auto space-y-3 bg-gray-50"
          >
            {messages.map((msg, i) => (
              <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className="flex flex-col max-w-[80%]">
                  <div
                    className={`p-3 rounded-2xl text-sm leading-relaxed ${
                      msg.role === 'user'
                        ? 'bg-[#00d09c] text-white rounded-tr-none'
                        : 'bg-white text-gray-800 shadow-sm border border-gray-100 rounded-tl-none'
                    }`}
                  >
                    {renderContent(msg.content)}
                  </div>
                  {msg.ts > 0 && (
                    <span
                      className={`text-[10px] text-gray-400 mt-1 ${
                        msg.role === 'user' ? 'text-right' : 'text-left'
                      }`}
                    >
                      {formatTime(msg.ts)}
                    </span>
                  )}
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="flex justify-start" aria-label="Assistant is typing">
                <div className="bg-white shadow-sm border border-gray-100 rounded-2xl rounded-tl-none p-3 flex items-center gap-1">
                  <span className="w-2 h-2 bg-gray-300 rounded-full animate-bounce [animation-delay:-0.3s]" />
                  <span className="w-2 h-2 bg-gray-300 rounded-full animate-bounce [animation-delay:-0.15s]" />
                  <span className="w-2 h-2 bg-gray-300 rounded-full animate-bounce" />
                </div>
              </div>
            )}

            {/* Suggested questions for first-time users */}
            {showSuggestions && (
              <div className="pt-1">
                <p className="text-[11px] text-gray-400 mb-2 ml-1">Try asking</p>
                <div className="flex flex-wrap gap-2">
                  {SUGGESTIONS.map((q, i) => (
                    <button
                      key={i}
                      onClick={() => sendMessage(q)}
                      className="text-left text-xs bg-white border border-gray-200 text-gray-700 px-3 py-1.5 rounded-full hover:border-[#00d09c] hover:text-[#00d09c] transition-colors"
                    >
                      {q}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Input */}
          <div className="p-3 border-t border-gray-100 bg-white">
            <div className="flex items-end gap-2">
              <textarea
                ref={inputRef}
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                rows={1}
                placeholder="Ask about HDFC funds..."
                aria-label="Type your question"
                className="flex-1 resize-none p-2 bg-gray-50 border-none rounded-lg text-sm focus:ring-1 focus:ring-[#00d09c] outline-none max-h-24"
              />
              <button
                onClick={() => sendMessage(input)}
                disabled={!input.trim() || isLoading}
                aria-label="Send message"
                className="p-2 w-9 h-9 flex items-center justify-center text-white bg-[#00d09c] rounded-full transition-colors disabled:bg-gray-200 disabled:text-gray-400 hover:bg-[#00b386]"
              >
                ➤
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

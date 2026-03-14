import { useState, useRef, useEffect, type ChangeEvent, type FormEvent } from 'react';
import { Send, Sparkles } from 'lucide-react';
import { Card, CardContent } from '../common/Card';
import { MessageBubble } from './MessageBubble';
import { ragService } from '../../services/api';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
}

export function QuerySection() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isLoading]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await ragService.query(userMessage.content);
      
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.answer || JSON.stringify(response),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error: unknown) {
      const err = error as { response?: { data?: { message?: string } }; message?: string };
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `Error: ${err.response?.data?.message || err.message || 'Failed to get answer.'}`,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    setInput(e.target.value);
  };

  return (
    <Card className="flex flex-col h-[600px]">
      <div className="flex items-center gap-2 p-4 border-b border-slate-700/50">
        <Sparkles className="w-5 h-5 text-indigo-400" />
        <h2 className="font-semibold text-slate-100">Ask the Database</h2>
      </div>

      <CardContent className="flex-1 overflow-y-auto p-4 space-y-6" ref={scrollRef}>
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-slate-500 space-y-4">
            <Sparkles className="w-12 h-12 text-slate-700/50" />
            <p className="text-sm">Ask a question to start exploring your documents.</p>
          </div>
        ) : (
          messages.map((message) => (
             <MessageBubble key={message.id} role={message.role} content={message.content} />
          ))
        )}

        {isLoading && (
          <MessageBubble
            role="assistant"
            content={
              <div className="flex gap-2 items-center h-5">
                <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce [animation-delay:-0.3s]" />
                <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce [animation-delay:-0.15s]" />
                <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" />
              </div>
            }
          />
        )}
      </CardContent>

      <div className="p-4 border-t border-slate-700/50">
        <form onSubmit={handleSubmit} className="relative flex items-center">
          <input
            type="text"
            value={input}
            onChange={handleInputChange}
            placeholder="e.g. What is Semantic Information Extraction?"
            className="w-full bg-slate-800 border border-slate-700 rounded-xl px-4 py-3 pr-12 text-sm text-slate-200 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition-all"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="absolute right-2 p-2 rounded-lg bg-indigo-600 text-white disabled:opacity-50 disabled:bg-slate-700 transition-colors"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </Card>
  );
}

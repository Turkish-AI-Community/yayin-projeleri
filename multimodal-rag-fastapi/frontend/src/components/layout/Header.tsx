import { Bot } from 'lucide-react';

export function Header() {
  return (
    <header className="sticky top-0 z-50 w-full border-b border-slate-700/50 bg-slate-900/80 backdrop-blur supports-backdrop-filter:bg-slate-900/60">
      <div className="container flex h-16 items-center px-4 md:px-6">
        <div className="flex gap-2 items-center">
          <div className="p-2 bg-indigo-600 rounded-lg">
            <Bot className="w-5 h-5 text-white" />
          </div>
          <span className="text-xl pl-2 font-bold bg-clip-text text-transparent bg-linear-to-r from-indigo-400 to-purple-400">
            Multimodal RAG Agent
          </span>
        </div>
      </div>
    </header>
  );
}

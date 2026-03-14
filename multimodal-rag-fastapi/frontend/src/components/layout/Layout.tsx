import { type ReactNode } from 'react';
import { Header } from './Header';

interface LayoutProps {
  children: ReactNode;
}

export function Layout({ children }: LayoutProps) {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-50 font-sans antialiased selection:bg-indigo-500/30 selection:text-indigo-200">
      <div className="fixed inset-0 bg-[radial-gradient(ellipse_at_top,var(--tw-gradient-stops))] from-indigo-900/20 via-slate-950/0 to-slate-950/0 pointer-events-none" />
      <Header />
      <main className="container relative mx-auto p-4 md:p-6 lg:p-8 max-w-7xl animate-in fade-in duration-500">
        {children}
      </main>
    </div>
  );
}

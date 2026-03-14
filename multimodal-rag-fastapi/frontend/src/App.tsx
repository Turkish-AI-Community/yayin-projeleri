import { Layout } from './components/layout/Layout';
import { EmbedSection } from './components/features/EmbedSection';
import { QuerySection } from './components/features/QuerySection';
import './index.css';

function App() {
  return (
    <Layout>
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 lg:gap-8">
        <div className="lg:col-span-4 flex flex-col gap-6">
          <div className="bg-linear-to-br from-indigo-500/20 to-purple-500/10 rounded-2xl p-6 border border-indigo-500/20 glass supports-backdrop-filter:bg-indigo-500/5">
            <h1 className="text-2xl font-bold text-white mb-2">
              Welcome back
            </h1>
            <p className="text-sm text-indigo-200/80 leading-relaxed">
              Explore your documents using advanced AI. Embed new knowledge or
              query the existing vector store with multimodal capabilities.
            </p>
          </div>
          
          <EmbedSection />
        </div>

        <div className="lg:col-span-8">
          <QuerySection />
        </div>
      </div>
    </Layout>
  );
}

export default App;

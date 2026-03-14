import { useState } from 'react';
import { Database, CheckCircle, AlertCircle } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '../common/Card';
import { Button } from '../common/Button';
import { ragService } from '../../services/api';
import { UploadZone } from './UploadZone';

export function EmbedSection() {
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [isUploading, setIsUploading] = useState(false);
  const [message, setMessage] = useState('');

  const handleUpload = async (file: File) => {
    try {
      setIsUploading(true);
      setStatus('loading');
      setMessage(`Uploading ${file.name}...`);
      
      const response = await ragService.uploadFile(file);
      
      setStatus('success');
      setMessage(response.message || 'File uploaded successfully!');
    } catch (err: unknown) {
      setStatus('error');
      const error = err as { response?: { data?: { message?: string } }; message?: string };
      setMessage(
        error.response?.data?.message || error.message || 'Failed to upload file.'
      );
    } finally {
      setIsUploading(false);
    }
  };

  const handleEmbed = async () => {
    try {
      setStatus('loading');
      setMessage('Starting embedding process...');
      
      const response = await ragService.embedDocuments();
      setMessage(response.message);
      
      // Polling for completion
      const pollStatus = async () => {
        const check = await ragService.getEmbeddingStatus();
        if (check.embedding_in_progress) {
          setMessage('Embedding in progress. Indexing multimodal data...');
          setTimeout(pollStatus, 2000); // Poll every 2 seconds
        } else {
          setStatus('success');
          setMessage('Embedding process is done. You can query your documents.');
        }
      };
      
      setTimeout(pollStatus, 1000);
    } catch (err: unknown) {
      setStatus('error');
      const error = err as { response?: { data?: { message?: string } }; message?: string };
      setMessage(
        error.response?.data?.message || error.message || 'Failed to embed documents.'
      );
    }
  };

  return (
    <Card className="h-full flex flex-col">
      <CardHeader>
        <div className="flex items-center gap-2">
          <Database className="w-5 h-5 text-indigo-400" />
          <CardTitle>Knowledge Base</CardTitle>
        </div>
      </CardHeader>
      
      <CardContent className="flex-1 space-y-6">
        <p className="text-slate-400 text-sm text-center">
          Index PDFs (6-pg chunks), Images, Video (up to 120s), and Audio 
          directly into the Knowledge Base.
        </p>

        <UploadZone onUpload={handleUpload} isUploading={isUploading} />
        
        {status !== 'idle' && (
          <div
            className={`p-4 rounded-lg text-sm border flex items-start gap-3 transition-all duration-300 ${
              status === 'loading'
                ? 'bg-blue-500/10 border-blue-500/20 text-blue-200'
                : status === 'success'
                ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-200'
                : 'bg-rose-500/10 border-rose-500/20 text-rose-200'
            }`}
          >
            {status === 'success' && <CheckCircle className="w-5 h-5 shrink-0" />}
            {status === 'error' && <AlertCircle className="w-5 h-5 shrink-0" />}
            {status === 'loading' && (
              <div className="w-5 h-5 border-2 border-blue-400 border-t-transparent rounded-full animate-spin shrink-0" />
            )}
            <p>{message}</p>
          </div>
        )}
      </CardContent>

      <CardFooter className="justify-center pt-4 border-t border-slate-700/50">
        <Button
          onClick={handleEmbed}
          isLoading={status === 'loading' && !isUploading}
          disabled={isUploading}
          className="w-full"
        >
          {status === 'loading' && !isUploading ? 'Indexing Documents...' : 'Start Embedding'}
        </Button>
      </CardFooter>
    </Card>
  );
}

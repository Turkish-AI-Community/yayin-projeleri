import React, { useState, useRef } from 'react';
import { Upload, X, FileText, CheckCircle2, Image as ImageIcon, Film, Music } from 'lucide-react';
import { cn } from '../../utils/cn';
import { Button } from '../common/Button';

interface UploadZoneProps {
  onUpload: (file: File) => Promise<void>;
  isUploading: boolean;
}

export function UploadZone({ onUpload, isUploading }: UploadZoneProps) {
  const [dragActive, setDragActive] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(e.type === 'dragenter' || e.type === 'dragover');
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    const droppedFile = e.dataTransfer.files?.[0];
    if (droppedFile) {
      const allowed = [
        'application/pdf',
        'image/png',
        'image/jpeg',
        'video/mp4',
        'video/quicktime',
        'audio/mpeg',
        'audio/wav',
        'audio/x-m4a'
      ];
      if (allowed.includes(droppedFile.type)) {
        setFile(droppedFile);
      }
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) setFile(e.target.files[0]);
  };

  const getFileIcon = () => {
    if (!file) return null;
    const type = file.type;
    if (type.startsWith('image/')) return <ImageIcon className="w-6 h-6 text-emerald-400" />;
    if (type.startsWith('video/')) return <Film className="w-6 h-6 text-emerald-400" />;
    if (type.startsWith('audio/')) return <Music className="w-6 h-6 text-emerald-400" />;
    return <FileText className="w-6 h-6 text-emerald-400" />;
  };

  const renderContent = () => {
    if (file) {
      return (
        <div className="flex flex-col items-center gap-3 animate-in fade-in zoom-in duration-300">
          <div className="w-12 h-12 rounded-full bg-emerald-500/20 flex items-center justify-center">
            {getFileIcon()}
          </div>
          <div className="text-center w-full max-w-[200px]">
            <p className="text-slate-200 font-medium truncate">{file.name}</p>
            <p className="text-slate-400 text-xs">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
          </div>
          <button
            onClick={(e) => { e.stopPropagation(); setFile(null); }}
            className="absolute top-3 right-3 p-1 rounded-full hover:bg-slate-700 text-slate-400 hover:text-slate-200"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      );
    }
    return (
      <>
        <div className="w-12 h-12 rounded-full bg-slate-700 flex items-center justify-center group-hover:bg-indigo-600 transition-colors duration-300">
          <Upload className="w-6 h-6 text-slate-300 group-hover:text-white" />
        </div>
        <div className="text-center">
          <p className="text-slate-200 font-medium">Click to upload or drag and drop</p>
          <p className="text-slate-400 text-sm mt-1">PDF, Images, Video, Audio</p>
        </div>
      </>
    );
  };

  return (
    <div className="space-y-4">
      <div
        className={cn(
          'relative border-2 border-dashed rounded-xl p-8 transition-all duration-300 flex flex-col items-center justify-center gap-4 group cursor-pointer',
          dragActive ? 'border-indigo-500 bg-indigo-500/10' : 'border-slate-700 hover:border-slate-500 bg-slate-800/50 hover:bg-slate-800/80',
          file && 'border-emerald-500/50 bg-emerald-500/5'
        )}
        onDragEnter={handleDrag} onDragLeave={handleDrag} onDragOver={handleDrag} onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
      >
        <input ref={inputRef} type="file" className="hidden" accept=".pdf,.png,.jpg,.jpeg,.mp4,.mov,.mp3,.wav,.m4a" onChange={handleChange} />
        {renderContent()}
      </div>
      {file && (
        <Button className="w-full h-11 gap-2" onClick={async () => { await onUpload(file); setFile(null); }} isLoading={isUploading}>
          <CheckCircle2 className="w-4 h-4" />
          Confirm Upload
        </Button>
      )}
    </div>
  );
}

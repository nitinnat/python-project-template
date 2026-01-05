import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  FolderOpen,
  FileText,
  FileSpreadsheet,
  FileImage,
  File,
  RefreshCw,
  Upload,
  CheckCircle,
  XCircle,
  Clock,
  Loader2,
} from 'lucide-react';
import { listFolderDocuments, getDocumentStatus, ingestFolder } from '@/api/rag';
import { FileInfo, DocumentStatus, IngestProgress } from '@/api/ragTypes';

interface DocumentsTabProps {
  folderPath: string;
  onFolderPathChange: (path: string) => void;
}

function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function getFileIcon(type: string) {
  switch (type) {
    case 'pdf':
      return <FileText className="w-5 h-5 text-red-500" />;
    case 'docx':
      return <FileText className="w-5 h-5 text-blue-500" />;
    case 'xlsx':
      return <FileSpreadsheet className="w-5 h-5 text-green-500" />;
    case 'pptx':
      return <FileImage className="w-5 h-5 text-orange-500" />;
    case 'md':
    case 'txt':
      return <FileText className="w-5 h-5 text-gray-500" />;
    default:
      return <File className="w-5 h-5 text-gray-400" />;
  }
}

function getStatusIcon(status: string) {
  switch (status) {
    case 'completed':
      return <CheckCircle className="w-4 h-4 text-green-500" />;
    case 'failed':
      return <XCircle className="w-4 h-4 text-red-500" />;
    case 'processing':
      return <Loader2 className="w-4 h-4 text-blue-500 animate-spin" />;
    default:
      return <Clock className="w-4 h-4 text-gray-400" />;
  }
}

export function DocumentsTab({ folderPath, onFolderPathChange }: DocumentsTabProps) {
  const queryClient = useQueryClient();
  const [inputPath, setInputPath] = useState(folderPath);
  const [isIngesting, setIsIngesting] = useState(false);
  const [ingestProgress, setIngestProgress] = useState<IngestProgress | null>(null);

  useEffect(() => {
    setInputPath(folderPath);
  }, [folderPath]);

  const {
    data: folderContents,
    isLoading: isLoadingFiles,
    error: filesError,
    refetch: refetchFiles,
  } = useQuery({
    queryKey: ['folder-documents', folderPath],
    queryFn: () => listFolderDocuments(folderPath),
    enabled: !!folderPath,
  });

  const {
    data: documentStatus,
    isLoading: isLoadingStatus,
    refetch: refetchStatus,
  } = useQuery({
    queryKey: ['document-status', folderPath],
    queryFn: () => getDocumentStatus(folderPath),
    enabled: !!folderPath,
    refetchInterval: isIngesting ? 2000 : false,
  });

  const handlePathSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputPath.trim()) {
      onFolderPathChange(inputPath.trim());
    }
  };

  const handleIngest = async () => {
    if (!folderPath) return;

    setIsIngesting(true);
    setIngestProgress(null);

    try {
      for await (const progress of ingestFolder(folderPath)) {
        setIngestProgress(progress);
        if (progress.type === 'complete') {
          break;
        }
      }
    } catch (error) {
      console.error('Ingestion failed:', error);
      setIngestProgress({
        type: 'error',
        error: error instanceof Error ? error.message : 'Ingestion failed',
        total: 0,
        processed: 0,
        status: 'completed',
      });
    } finally {
      setIsIngesting(false);
      refetchStatus();
      queryClient.invalidateQueries({ queryKey: ['folder-documents', folderPath] });
    }
  };

  const statusMap = new Map(
    documentStatus?.map((doc) => [doc.file_name, doc]) || []
  );

  return (
    <div className="h-full flex flex-col">
      {/* Folder Path Input */}
      <form onSubmit={handlePathSubmit} className="mb-6">
        <div className="flex gap-4">
          <div className="flex-1 relative">
            <FolderOpen className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              value={inputPath}
              onChange={(e) => setInputPath(e.target.value)}
              placeholder="Enter folder path (e.g., /documents)"
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
          </div>
          <button
            type="submit"
            className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
          >
            Load Folder
          </button>
        </div>
        <p className="mt-2 text-sm text-gray-600">
          💡 Tip: Place your files in the configured documents folder (default <code className="px-1.5 py-0.5 bg-gray-100 rounded text-xs">./documents</code> on host, <code className="px-1.5 py-0.5 bg-gray-100 rounded text-xs">/documents</code> in Docker) and use that path here.
        </p>
      </form>

      {/* Actions Bar */}
      {folderPath && (
        <div className="flex items-center justify-between mb-4">
          <div className="text-sm text-gray-600">
            {folderContents?.total_count || 0} documents found
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => {
                refetchFiles();
                refetchStatus();
              }}
              disabled={isLoadingFiles || isLoadingStatus}
              className="flex items-center gap-2 px-3 py-1.5 text-sm text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 ${isLoadingFiles ? 'animate-spin' : ''}`} />
              Refresh
            </button>
            <button
              onClick={handleIngest}
              disabled={isIngesting || !folderContents?.files?.length}
              className="flex items-center gap-2 px-4 py-1.5 text-sm text-white bg-green-600 rounded-lg hover:bg-green-700 disabled:opacity-50"
            >
              {isIngesting ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Upload className="w-4 h-4" />
              )}
              {isIngesting ? 'Ingesting...' : 'Ingest All'}
            </button>
          </div>
        </div>
      )}

      {/* Progress Bar */}
      {ingestProgress && (
        <div className="mb-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">
              {ingestProgress.type === 'error'
                ? 'Error'
                : ingestProgress.type === 'complete'
                ? 'Complete'
                : `Processing: ${ingestProgress.current_file || '...'}`}
            </span>
            <span className="text-sm text-gray-500">
              {ingestProgress.processed} / {ingestProgress.total}
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full transition-all ${
                ingestProgress.type === 'error'
                  ? 'bg-red-500'
                  : ingestProgress.type === 'complete'
                  ? 'bg-green-500'
                  : 'bg-primary-500'
              }`}
              style={{
                width: `${
                  ingestProgress.total > 0
                    ? (ingestProgress.processed / ingestProgress.total) * 100
                    : 0
                }%`,
              }}
            />
          </div>
          {ingestProgress.error && (
            <p className="mt-2 text-sm text-red-600">{ingestProgress.error}</p>
          )}
        </div>
      )}

      {/* Document List */}
      <div className="flex-1 overflow-auto">
        {!folderPath ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-500">
            <FolderOpen className="w-16 h-16 mb-4 text-gray-300" />
            <p className="text-lg font-medium mb-2">Get Started with Document Chat</p>
            <div className="max-w-md text-sm space-y-3 text-left">
              <div className="p-3 bg-blue-50 rounded-lg border border-blue-200">
                <p className="font-medium text-blue-900 mb-1">📁 Step 1: Add Your Documents</p>
                <p className="text-blue-800">Copy your files to the <code className="px-1 bg-white rounded text-xs">./documents/</code> folder in the project directory</p>
              </div>
              <div className="p-3 bg-green-50 rounded-lg border border-green-200">
                <p className="font-medium text-green-900 mb-1">🔗 Step 2: Load Folder</p>
                <p className="text-green-800">Enter <code className="px-1 bg-white rounded text-xs">/documents</code> above and click "Load Folder"</p>
              </div>
              <div className="p-3 bg-purple-50 rounded-lg border border-purple-200">
                <p className="font-medium text-purple-900 mb-1">📝 Supported Formats</p>
                <p className="text-purple-800">PDF, DOCX, PPTX, XLSX, TXT, MD</p>
              </div>
            </div>
          </div>
        ) : isLoadingFiles ? (
          <div className="flex items-center justify-center h-full">
            <Loader2 className="w-8 h-8 text-primary-500 animate-spin" />
          </div>
        ) : filesError ? (
          <div className="flex flex-col items-center justify-center h-full text-red-500">
            <XCircle className="w-16 h-16 mb-4" />
            <p className="text-lg">Failed to load folder</p>
            <p className="text-sm mt-1">
              {filesError instanceof Error ? filesError.message : 'Unknown error'}
            </p>
          </div>
        ) : !folderContents?.files?.length ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-500">
            <FileText className="w-16 h-16 mb-4 text-gray-300" />
            <p className="text-lg">No supported documents found</p>
            <p className="text-sm mt-1">Add PDF, DOCX, PPTX, XLSX, TXT, or MD files to this folder</p>
          </div>
        ) : (
          <div className="border border-gray-200 rounded-lg overflow-hidden">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Document
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Type
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Size
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Modified
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Chunks
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {folderContents.files.map((file) => {
                  const status = statusMap.get(file.name);
                  return (
                    <tr key={file.path} className="hover:bg-gray-50">
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-3">
                          {getFileIcon(file.type)}
                          <span className="text-sm font-medium text-gray-900 truncate max-w-xs">
                            {file.name}
                          </span>
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <span className="text-sm text-gray-500 uppercase">{file.type}</span>
                      </td>
                      <td className="px-4 py-3">
                        <span className="text-sm text-gray-500">{formatFileSize(file.size)}</span>
                      </td>
                      <td className="px-4 py-3">
                        <span className="text-sm text-gray-500">{formatDate(file.modified_at)}</span>
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-2">
                          {getStatusIcon(status?.status || 'pending')}
                          <span className="text-sm text-gray-600 capitalize">
                            {status?.status || 'Not ingested'}
                          </span>
                        </div>
                        {status?.error_message && (
                          <p className="text-xs text-red-500 mt-1 truncate max-w-xs" title={status.error_message}>
                            {status.error_message}
                          </p>
                        )}
                      </td>
                      <td className="px-4 py-3">
                        <span className="text-sm text-gray-500">
                          {status?.chunk_count || '-'}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

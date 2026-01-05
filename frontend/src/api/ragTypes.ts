/**
 * RAG API type definitions
 */

// ============================================================================
// Document Types
// ============================================================================

export interface FileInfo {
  name: string;
  path: string;
  type: string;
  size: number;
  modified_at: string;
}

export interface FolderContents {
  folder_path: string;
  files: FileInfo[];
  total_count: number;
}

export interface DocumentIngestRequest {
  folder_path: string;
}

export interface DocumentStatus {
  id: string;
  file_name: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  chunk_count: number;
  error_message: string | null;
  created_at: string;
}

export interface IngestProgress {
  type: 'progress' | 'error' | 'complete';
  total: number;
  processed: number;
  current_file?: string;
  status: 'running' | 'completed';
  error?: string;
  file?: string;
}

// ============================================================================
// Chat Types
// ============================================================================

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface ChatSource {
  document_name: string;
  chunk_content: string;
  relevance_score: number;
}

export interface ChatRequest {
  message: string;
  conversation_id?: string;
  folder_path?: string;
}

export interface ChatResponse {
  conversation_id: string;
  message: string;
  sources: ChatSource[];
}

export interface ChatStreamEvent {
  type: 'sources' | 'message' | 'done' | 'error';
  sources?: ChatSource[];
  content?: string;
  conversation_id?: string;
  error?: string;
}

// ============================================================================
// Conversation Types
// ============================================================================

export interface ConversationSummary {
  id: string;
  title: string | null;
  folder_path: string | null;
  created_at: string;
  message_count: number;
}

export interface ConversationDetail {
  id: string;
  title: string | null;
  folder_path: string | null;
  messages: ChatMessage[];
  created_at: string;
}

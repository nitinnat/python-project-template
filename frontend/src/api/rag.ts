import apiClient from './client';
import {
  ChatRequest,
  ChatResponse,
  ChatStreamEvent,
  ConversationDetail,
  ConversationSummary,
  DocumentStatus,
  FolderContents,
  IngestProgress,
} from './ragTypes';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export async function listFolderDocuments(folderPath: string): Promise<FolderContents> {
  const response = await apiClient.get<FolderContents>('/rag/documents/folder', {
    params: { folder_path: folderPath },
  });
  return response.data;
}

export async function* ingestFolder(folderPath: string): AsyncGenerator<IngestProgress> {
  const response = await fetch(`${API_BASE}/rag/documents/ingest`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${localStorage.getItem('access_token') || ''}`,
    },
    body: JSON.stringify({ folder_path: folderPath }),
  });

  if (!response.ok) {
    throw new Error(`Ingestion failed: ${response.statusText}`);
  }

  const reader = response.body?.getReader();
  if (!reader) {
    throw new Error('No response body');
  }

  const decoder = new TextDecoder();
  let buffer = '';

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6);
          try {
            const event = JSON.parse(data) as IngestProgress;
            yield event;
          } catch (e) {
            console.error('Failed to parse SSE event:', data);
          }
        }
      }
    }
  } finally {
    reader.releaseLock();
  }
}

export async function getDocumentStatus(folderPath: string): Promise<DocumentStatus[]> {
  const response = await apiClient.get<DocumentStatus[]>('/rag/documents/status', {
    params: { folder_path: folderPath },
  });
  return response.data;
}

export async function chat(request: ChatRequest): Promise<ChatResponse> {
  const response = await apiClient.post<ChatResponse>('/rag/chat', request, {
    timeout: 180000,
  });
  return response.data;
}

export async function* chatStream(request: ChatRequest): AsyncGenerator<ChatStreamEvent> {
  const response = await fetch(`${API_BASE}/rag/chat/stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${localStorage.getItem('access_token') || ''}`,
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error(`Chat failed: ${response.statusText}`);
  }

  const reader = response.body?.getReader();
  if (!reader) {
    throw new Error('No response body');
  }

  const decoder = new TextDecoder();
  let buffer = '';

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6);
          try {
            const event = JSON.parse(data) as ChatStreamEvent;
            yield event;
          } catch (e) {
            console.error('Failed to parse SSE event:', data);
          }
        }
      }
    }
  } finally {
    reader.releaseLock();
  }
}

export async function listConversations(limit: number = 20): Promise<ConversationSummary[]> {
  const response = await apiClient.get<ConversationSummary[]>('/rag/conversations', {
    params: { limit },
  });
  return response.data;
}

export async function getConversation(conversationId: string): Promise<ConversationDetail> {
  const response = await apiClient.get<ConversationDetail>(
    `/rag/conversations/${conversationId}`
  );
  return response.data;
}

export async function deleteConversation(conversationId: string): Promise<void> {
  await apiClient.delete(`/rag/conversations/${conversationId}`);
}

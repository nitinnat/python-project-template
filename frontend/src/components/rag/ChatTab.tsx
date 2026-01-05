import { useState, useEffect, useRef } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
  Send,
  Loader2,
  MessageSquare,
  ChevronDown,
  ChevronRight,
  FileText,
  Trash2,
  Plus,
} from 'lucide-react';
import {
  chat,
  listConversations,
  getConversation,
  deleteConversation,
} from '@/api/rag';
import {
  ChatMessage,
  ChatSource,
  ConversationSummary,
} from '@/api/ragTypes';

interface ChatTabProps {
  folderPath: string;
}

function SourceCard({ source, isExpanded, onToggle }: {
  source: ChatSource;
  isExpanded: boolean;
  onToggle: () => void;
}) {
  return (
    <div className="border border-gray-200 rounded-lg overflow-hidden">
      <button
        onClick={onToggle}
        className="w-full flex items-center justify-between px-3 py-2 bg-gray-50 hover:bg-gray-100 transition-colors"
      >
        <div className="flex items-center gap-2 text-sm">
          <FileText className="w-4 h-4 text-gray-400" />
          <span className="font-medium text-gray-700">{source.document_name}</span>
          <span className="text-gray-400">
            ({(source.relevance_score * 100).toFixed(0)}% match)
          </span>
        </div>
        {isExpanded ? (
          <ChevronDown className="w-4 h-4 text-gray-400" />
        ) : (
          <ChevronRight className="w-4 h-4 text-gray-400" />
        )}
      </button>
      {isExpanded && (
        <div className="px-3 py-2 text-sm text-gray-600 bg-white border-t border-gray-200 max-h-40 overflow-auto">
          <pre className="whitespace-pre-wrap font-sans">{source.chunk_content}</pre>
        </div>
      )}
    </div>
  );
}

function MessageBubble({ message, sources }: {
  message: ChatMessage;
  sources?: ChatSource[];
}) {
  const [expandedSources, setExpandedSources] = useState<Set<number>>(new Set());
  const isUser = message.role === 'user';

  const toggleSource = (index: number) => {
    setExpandedSources((prev) => {
      const next = new Set(prev);
      if (next.has(index)) {
        next.delete(index);
      } else {
        next.add(index);
      }
      return next;
    });
  };

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[80%] ${
          isUser
            ? 'bg-primary-600 text-white rounded-2xl rounded-tr-sm'
            : 'bg-white border border-gray-200 rounded-2xl rounded-tl-sm'
        } px-4 py-3`}
      >
        {isUser ? (
          <p className="text-sm">{message.content}</p>
        ) : (
          <div className="prose prose-sm max-w-none text-gray-800">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {message.content}
            </ReactMarkdown>
          </div>
        )}

        {/* Sources */}
        {!isUser && sources && sources.length > 0 && (
          <div className="mt-3 pt-3 border-t border-gray-200 space-y-2">
            <p className="text-xs font-medium text-gray-500 uppercase">Sources</p>
            {sources.map((source, idx) => (
              <SourceCard
                key={idx}
                source={source}
                isExpanded={expandedSources.has(idx)}
                onToggle={() => toggleSource(idx)}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export function ChatTab({ folderPath }: ChatTabProps) {
  const queryClient = useQueryClient();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [input, setInput] = useState('');
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [sources, setSources] = useState<ChatSource[]>([]);
  const [showSidebar, setShowSidebar] = useState(true);

  const { data: conversations, refetch: refetchConversations } = useQuery({
    queryKey: ['conversations'],
    queryFn: () => listConversations(20),
  });

  const loadConversationMutation = useMutation({
    mutationFn: getConversation,
    onSuccess: (data) => {
      setConversationId(data.id);
      setMessages(data.messages);
      setSources([]);
    },
  });

  const chatMutation = useMutation({
    mutationFn: chat,
    onSuccess: (response) => {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: response.message },
      ]);
      setSources(response.sources);
      setConversationId(response.conversation_id);
      refetchConversations();
    },
  });

  const deleteConversationMutation = useMutation({
    mutationFn: deleteConversation,
    onSuccess: () => {
      refetchConversations();
      if (conversationId) {
        handleNewConversation();
      }
    },
  });

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleNewConversation = () => {
    setConversationId(null);
    setMessages([]);
    setSources([]);
    setInput('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || chatMutation.isPending) return;

    const userMessage = input.trim();
    setInput('');
    setMessages((prev) => [...prev, { role: 'user', content: userMessage }]);
    setSources([]);

    chatMutation.mutate({
      message: userMessage,
      conversation_id: conversationId || undefined,
      folder_path: folderPath || undefined,
    });
  };

  const handleConversationClick = (conv: ConversationSummary) => {
    loadConversationMutation.mutate(conv.id);
  };

  const handleDeleteConversation = (e: React.MouseEvent, convId: string) => {
    e.stopPropagation();
    if (confirm('Delete this conversation?')) {
      deleteConversationMutation.mutate(convId);
    }
  };

  return (
    <div className="h-full flex">
      {/* Sidebar */}
      {showSidebar && (
        <div className="w-64 border-r border-gray-200 flex flex-col bg-gray-50">
          <div className="p-3 border-b border-gray-200">
            <button
              onClick={handleNewConversation}
              className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
            >
              <Plus className="w-4 h-4" />
              New Chat
            </button>
          </div>
          <div className="flex-1 overflow-auto p-2 space-y-1">
            {conversations?.map((conv) => (
              <div
                key={conv.id}
                onClick={() => handleConversationClick(conv)}
                className={`group flex items-center justify-between px-3 py-2 rounded-lg cursor-pointer transition-colors ${
                  conversationId === conv.id
                    ? 'bg-primary-100 text-primary-800'
                    : 'hover:bg-gray-100 text-gray-700'
                }`}
              >
                <div className="flex items-center gap-2 min-w-0">
                  <MessageSquare className="w-4 h-4 flex-shrink-0" />
                  <span className="text-sm truncate">
                    {conv.title || 'New conversation'}
                  </span>
                </div>
                <button
                  onClick={(e) => handleDeleteConversation(e, conv.id)}
                  className="opacity-0 group-hover:opacity-100 p-1 hover:bg-red-100 rounded transition-opacity"
                >
                  <Trash2 className="w-3 h-3 text-red-500" />
                </button>
              </div>
            ))}
            {conversations?.length === 0 && (
              <p className="text-sm text-gray-500 text-center py-4">
                No conversations yet
              </p>
            )}
          </div>
        </div>
      )}

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Toggle Sidebar Button */}
        <button
          onClick={() => setShowSidebar(!showSidebar)}
          className="absolute left-0 top-1/2 -translate-y-1/2 p-1 bg-white border border-gray-200 rounded-r-lg shadow-sm hover:bg-gray-50 z-10"
        >
          {showSidebar ? (
            <ChevronRight className="w-4 h-4 text-gray-400" />
          ) : (
            <ChevronDown className="w-4 h-4 text-gray-400 rotate-90" />
          )}
        </button>

        {/* Messages */}
        <div className="flex-1 overflow-auto p-4 space-y-4">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-gray-500">
              <MessageSquare className="w-16 h-16 mb-4 text-gray-300" />
              <p className="text-lg font-medium">Start a conversation</p>
              <p className="text-sm mt-1">
                {folderPath
                  ? 'Ask questions about your documents'
                  : 'Select a folder in the Documents tab first'}
              </p>
            </div>
          ) : (
            <>
              {messages.map((msg, idx) => (
                <MessageBubble
                  key={idx}
                  message={msg}
                  sources={
                    msg.role === 'assistant' && idx === messages.length - 1
                      ? sources
                      : undefined
                  }
                />
              ))}
              {chatMutation.isPending && (
                <div className="flex justify-start">
                  <div className="bg-white border border-gray-200 rounded-2xl rounded-tl-sm px-4 py-3">
                    <Loader2 className="w-5 h-5 text-gray-400 animate-spin" />
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        {/* Input */}
        <form onSubmit={handleSubmit} className="p-4 border-t border-gray-200 bg-white">
          <div className="flex gap-3">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={
                folderPath
                  ? 'Ask a question about your documents...'
                  : 'Select a folder first to chat with documents'
              }
              disabled={chatMutation.isPending}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 disabled:bg-gray-100"
            />
            <button
              type="submit"
              disabled={!input.trim() || chatMutation.isPending}
              className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {chatMutation.isPending ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Send className="w-5 h-5" />
              )}
            </button>
          </div>
          {chatMutation.isError && (
            <p className="mt-2 text-sm text-red-600">
              {chatMutation.error instanceof Error
                ? chatMutation.error.message
                : 'Failed to send message'}
            </p>
          )}
        </form>
      </div>
    </div>
  );
}

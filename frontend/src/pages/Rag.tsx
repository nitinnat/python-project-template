import { useState, useEffect } from 'react';
import { FileText, MessageSquare } from 'lucide-react';
import { DocumentsTab } from '@/components/rag/DocumentsTab';
import { ChatTab } from '@/components/rag/ChatTab';

type TabType = 'documents' | 'chat';

const FOLDER_PATH_KEY = 'rag_folder_path';

export function RagPage() {
  const [activeTab, setActiveTab] = useState<TabType>('documents');
  const [folderPath, setFolderPath] = useState<string>(() => {
    return localStorage.getItem(FOLDER_PATH_KEY) || '';
  });

  useEffect(() => {
    if (folderPath) {
      localStorage.setItem(FOLDER_PATH_KEY, folderPath);
    }
  }, [folderPath]);

  const tabs = [
    { id: 'documents' as const, label: 'Documents', icon: FileText },
    { id: 'chat' as const, label: 'Chat', icon: MessageSquare },
  ];

  return (
    <div className="p-6 h-[calc(100vh-4rem)]">
      <div className="flex flex-col h-full">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900">Document Chat</h1>
          <p className="mt-1 text-gray-600">
            Ingest documents and chat with them using RAG
          </p>
        </div>

        {/* Tab Navigation */}
        <div className="border-b border-gray-200 mb-6">
          <nav className="-mb-px flex space-x-8">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`
                    group inline-flex items-center gap-2 py-4 px-1 border-b-2 font-medium text-sm
                    ${
                      isActive
                        ? 'border-primary-500 text-primary-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }
                  `}
                >
                  <Icon
                    className={`w-5 h-5 ${
                      isActive ? 'text-primary-500' : 'text-gray-400 group-hover:text-gray-500'
                    }`}
                  />
                  {tab.label}
                </button>
              );
            })}
          </nav>
        </div>

        {/* Tab Content */}
        <div className="flex-1 overflow-hidden">
          {activeTab === 'documents' && (
            <DocumentsTab
              folderPath={folderPath}
              onFolderPathChange={setFolderPath}
            />
          )}
          {activeTab === 'chat' && (
            <ChatTab folderPath={folderPath} />
          )}
        </div>
      </div>
    </div>
  );
}

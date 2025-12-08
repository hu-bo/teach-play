import { useState } from 'react';
import { X, Monitor } from 'lucide-react';
import { useWindows, useStartRecording } from '../hooks/useRecorder';
import { useAppStore } from '../stores/appStore';
import type { WindowInfo } from '../types';

interface Props {
  projectId: string;
  onClose: () => void;
  onSuccess?: () => void;
}

export default function WindowSelector({ projectId, onClose, onSuccess }: Props) {
  const { data: windows, isLoading } = useWindows();
  const startRecording = useStartRecording();
  const [selectedWindow, setSelectedWindow] = useState<WindowInfo | null>(null);
  const [recordingName, setRecordingName] = useState('');

  const handleStart = async () => {
    if (!selectedWindow) return;

    try {
      await startRecording.mutateAsync({
        projectId,
        windowId: selectedWindow.window_id,
        name: recordingName || undefined,
      });
      onSuccess?.();
      onClose();
    } catch (error) {
      console.error('Start recording failed:', error);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl shadow-xl w-[600px] max-h-[80vh] overflow-hidden">
        {/* 头部 */}
        <div className="flex items-center justify-between p-4 border-b">
          <h2 className="text-lg font-semibold">选择录制窗口</h2>
          <button
            onClick={onClose}
            className="p-1 hover:bg-gray-100 rounded"
          >
            <X size={20} />
          </button>
        </div>

        {/* 录制名称 */}
        <div className="p-4 border-b">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            录制名称 (可选)
          </label>
          <input
            type="text"
            value={recordingName}
            onChange={(e) => setRecordingName(e.target.value)}
            placeholder="输入录制名称..."
            className="input"
          />
        </div>

        {/* 窗口列表 */}
        <div className="p-4 max-h-[400px] overflow-auto">
          {isLoading ? (
            <div className="text-center text-gray-500 py-8">
              加载窗口列表中...
            </div>
          ) : windows?.length === 0 ? (
            <div className="text-center text-gray-500 py-8">
              没有找到可用窗口
            </div>
          ) : (
            <div className="grid grid-cols-2 gap-3">
              {windows?.map((window) => (
                <button
                  key={window.window_id}
                  onClick={() => setSelectedWindow(window)}
                  className={`p-3 border rounded-lg text-left transition-colors ${
                    selectedWindow?.window_id === window.window_id
                      ? 'border-primary-500 bg-primary-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="flex items-start gap-3">
                    {window.thumbnail ? (
                      <img
                        src={`data:image/png;base64,${window.thumbnail}`}
                        alt={window.title}
                        className="w-16 h-12 object-cover rounded border"
                      />
                    ) : (
                      <div className="w-16 h-12 bg-gray-100 rounded border flex items-center justify-center">
                        <Monitor size={24} className="text-gray-400" />
                      </div>
                    )}
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-sm truncate">
                        {window.title || '无标题'}
                      </p>
                      <p className="text-xs text-gray-500 truncate">
                        {window.process_name}
                      </p>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* 底部操作 */}
        <div className="flex justify-end gap-3 p-4 border-t bg-gray-50">
          <button onClick={onClose} className="btn btn-secondary">
            取消
          </button>
          <button
            onClick={handleStart}
            disabled={!selectedWindow || startRecording.isPending}
            className="btn btn-primary disabled:opacity-50"
          >
            {startRecording.isPending ? '启动中...' : '开始录制'}
          </button>
        </div>
      </div>
    </div>
  );
}

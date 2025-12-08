import { useState, useEffect } from 'react';
import { X, Sparkles } from 'lucide-react';
import type { Step, StepUpdate, StepMode } from '../types';

interface Props {
  step: Step;
  onSave: (data: StepUpdate) => void;
  onClose: () => void;
}

export default function StepEditor({ step, onSave, onClose }: Props) {
  const [mode, setMode] = useState<StepMode>(step.mode);
  const [description, setDescription] = useState(step.description || '');
  const [aiPrompt, setAiPrompt] = useState(step.ai_config?.prompt || '');

  const handleSave = () => {
    const update: StepUpdate = {
      mode,
      description,
    };

    if (mode === 'ai_decision') {
      update.ai_config = {
        prompt: aiPrompt,
        options: step.ai_config?.options || [],
      };
    }

    onSave(update);
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl shadow-xl w-[500px] max-h-[80vh] overflow-hidden">
        {/* 头部 */}
        <div className="flex items-center justify-between p-4 border-b">
          <h2 className="text-lg font-semibold">编辑步骤</h2>
          <button onClick={onClose} className="p-1 hover:bg-gray-100 rounded">
            <X size={20} />
          </button>
        </div>

        {/* 内容 */}
        <div className="p-4 space-y-4 overflow-auto">
          {/* 步骤信息 */}
          <div className="p-3 bg-gray-50 rounded-lg">
            <p className="text-sm text-gray-500">步骤类型</p>
            <p className="font-medium">{step.type}</p>
            {step.text && (
              <>
                <p className="text-sm text-gray-500 mt-2">识别文字</p>
                <p className="font-medium">{step.text}</p>
              </>
            )}
            {step.position && (
              <>
                <p className="text-sm text-gray-500 mt-2">坐标</p>
                <p className="font-medium">
                  ({step.position.x}, {step.position.y})
                </p>
              </>
            )}
          </div>

          {/* 执行模式 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              执行模式
            </label>
            <div className="grid grid-cols-3 gap-2">
              <button
                onClick={() => setMode('fixed')}
                className={`p-3 rounded-lg border text-center transition-colors ${
                  mode === 'fixed'
                    ? 'border-primary-500 bg-primary-50 text-primary-700'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <p className="font-medium text-sm">固定</p>
                <p className="text-xs text-gray-500">按坐标执行</p>
              </button>
              <button
                onClick={() => setMode('smart')}
                className={`p-3 rounded-lg border text-center transition-colors ${
                  mode === 'smart'
                    ? 'border-primary-500 bg-primary-50 text-primary-700'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <p className="font-medium text-sm">智能</p>
                <p className="text-xs text-gray-500">OCR/图像匹配</p>
              </button>
              <button
                onClick={() => setMode('ai_decision')}
                className={`p-3 rounded-lg border text-center transition-colors ${
                  mode === 'ai_decision'
                    ? 'border-purple-500 bg-purple-50 text-purple-700'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center justify-center gap-1">
                  <Sparkles size={14} />
                  <span className="font-medium text-sm">AI决策</span>
                </div>
                <p className="text-xs text-gray-500">AI分析决策</p>
              </button>
            </div>
          </div>

          {/* AI Prompt 配置 */}
          {mode === 'ai_decision' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                AI 决策 Prompt
              </label>
              <textarea
                value={aiPrompt}
                onChange={(e) => setAiPrompt(e.target.value)}
                rows={4}
                placeholder="描述AI需要做的决策，例如：分析三张卡片，选择攻击力最高的一张"
                className="input resize-none"
              />
              <p className="text-xs text-gray-500 mt-1">
                AI会根据此提示词分析屏幕截图并做出决策
              </p>
            </div>
          )}

          {/* 描述 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              步骤描述
            </label>
            <input
              type="text"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="输入步骤描述..."
              className="input"
            />
          </div>

          {/* 截图预览 */}
          {step.screenshot && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                截图
              </label>
              <img
                src={step.screenshot.replace(
                  'minio://',
                  'http://localhost:8000/api/files/'
                )}
                alt=""
                className="w-full rounded-lg border"
              />
            </div>
          )}
        </div>

        {/* 底部操作 */}
        <div className="flex justify-end gap-3 p-4 border-t bg-gray-50">
          <button onClick={onClose} className="btn btn-secondary">
            取消
          </button>
          <button onClick={handleSave} className="btn btn-primary">
            保存
          </button>
        </div>
      </div>
    </div>
  );
}

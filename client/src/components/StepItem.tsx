import {
  MousePointer,
  ScrollText,
  Move,
  Type,
  Keyboard,
  Clock,
  FileText,
  Sparkles,
  MoreVertical,
  Edit,
  Trash2,
} from 'lucide-react';
import { useState } from 'react';
import type { Step } from '../types';
import clsx from 'clsx';

interface Props {
  step: Step;
  isActive?: boolean;
  onClick?: () => void;
  onEdit?: () => void;
  onDelete?: () => void;
}

const stepIcons = {
  click: MousePointer,
  scroll: ScrollText,
  drag: Move,
  input: Type,
  key: Keyboard,
  wait: Clock,
  file_select: FileText,
};

const modeColors = {
  fixed: 'bg-gray-100 text-gray-600',
  smart: 'bg-blue-100 text-blue-600',
  ai_decision: 'bg-purple-100 text-purple-600',
};

const modeLabels = {
  fixed: '固定',
  smart: '智能',
  ai_decision: 'AI决策',
};

export default function StepItem({ step, isActive, onClick, onEdit, onDelete }: Props) {
  const [showMenu, setShowMenu] = useState(false);
  const Icon = stepIcons[step.type] || MousePointer;

  const getStepDescription = () => {
    switch (step.type) {
      case 'click':
        return step.text
          ? `点击 "${step.text}"`
          : `点击 (${step.position?.x}, ${step.position?.y})`;
      case 'scroll':
        return `${step.direction === 'up' ? '向上' : '向下'}滚动 ${step.amount}`;
      case 'drag':
        return `拖拽到 (${step.to?.x}, ${step.to?.y})`;
      case 'input':
        return `输入 "${step.input_text || step.text}"`;
      case 'key':
        return `按键 ${step.key}`;
      case 'wait':
        if (step.condition) {
          return `等待 ${step.condition.type === 'text_appear' ? '文字出现' : '图像匹配'}`;
        }
        return `等待 ${step.duration}ms`;
      case 'file_select':
        return `选择文件 ${step.file_path}`;
      default:
        return step.description || '未知操作';
    }
  };

  return (
    <div
      className={clsx(
        'group relative flex items-start gap-3 p-3 rounded-lg border transition-colors cursor-pointer',
        isActive
          ? 'border-primary-500 bg-primary-50'
          : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
      )}
      onClick={onClick}
    >
      {/* 序号 */}
      <div className="flex-shrink-0 w-6 h-6 rounded-full bg-gray-200 flex items-center justify-center text-xs font-medium">
        {step.index + 1}
      </div>

      {/* 图标 */}
      <div className="flex-shrink-0 w-8 h-8 rounded-lg bg-gray-100 flex items-center justify-center">
        <Icon size={18} className="text-gray-600" />
      </div>

      {/* 内容 */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="font-medium text-sm">{getStepDescription()}</span>
          {step.mode === 'ai_decision' && (
            <Sparkles size={14} className="text-purple-500" />
          )}
        </div>
        <div className="flex items-center gap-2 mt-1">
          <span
            className={clsx(
              'text-xs px-1.5 py-0.5 rounded',
              modeColors[step.mode]
            )}
          >
            {modeLabels[step.mode]}
          </span>
          {step.description && (
            <span className="text-xs text-gray-500 truncate">
              {step.description}
            </span>
          )}
        </div>
      </div>

      {/* 截图预览 */}
      {step.screenshot && (
        <div className="flex-shrink-0">
          <img
            src={step.screenshot.replace('minio://', 'http://localhost:8000/api/files/')}
            alt=""
            className="w-12 h-12 object-cover rounded border"
          />
        </div>
      )}

      {/* 操作菜单 */}
      <div className="relative">
        <button
          onClick={(e) => {
            e.stopPropagation();
            setShowMenu(!showMenu);
          }}
          className="p-1 rounded opacity-0 group-hover:opacity-100 hover:bg-gray-200 transition-opacity"
        >
          <MoreVertical size={16} />
        </button>

        {showMenu && (
          <>
            <div
              className="fixed inset-0 z-10"
              onClick={() => setShowMenu(false)}
            />
            <div className="absolute right-0 top-full mt-1 w-32 bg-white rounded-lg shadow-lg border z-20">
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onEdit?.();
                  setShowMenu(false);
                }}
                className="flex items-center gap-2 w-full px-3 py-2 text-sm text-left hover:bg-gray-100"
              >
                <Edit size={14} />
                编辑
              </button>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onDelete?.();
                  setShowMenu(false);
                }}
                className="flex items-center gap-2 w-full px-3 py-2 text-sm text-left text-red-600 hover:bg-red-50"
              >
                <Trash2 size={14} />
                删除
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

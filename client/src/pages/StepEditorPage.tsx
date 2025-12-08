import { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, Plus, Save } from 'lucide-react';
import { useRecording, useUpdateStep, useDeleteStep, useAddStep } from '../hooks/useRecordings';
import StepItem from '../components/StepItem';
import StepEditor from '../components/StepEditor';
import type { Step, StepUpdate } from '../types';

export default function StepEditorPage() {
  const { recordingId } = useParams<{ recordingId: string }>();
  const { data: recording, isLoading } = useRecording(recordingId!);
  const updateStep = useUpdateStep();
  const deleteStep = useDeleteStep();
  const addStep = useAddStep();
  const [editingStep, setEditingStep] = useState<Step | null>(null);
  const [showAddWait, setShowAddWait] = useState(false);

  const handleUpdateStep = async (data: StepUpdate) => {
    if (!editingStep) return;

    try {
      await updateStep.mutateAsync({
        recordingId: recordingId!,
        stepId: editingStep.id,
        step: data,
      });
      setEditingStep(null);
    } catch (error) {
      console.error('Update step failed:', error);
    }
  };

  const handleDeleteStep = async (stepId: string) => {
    if (!confirm('确定要删除此步骤吗？')) return;

    try {
      await deleteStep.mutateAsync({
        recordingId: recordingId!,
        stepId,
      });
    } catch (error) {
      console.error('Delete step failed:', error);
    }
  };

  const handleAddWaitStep = async (duration: number) => {
    try {
      await addStep.mutateAsync({
        recordingId: recordingId!,
        step: {
          type: 'wait',
          mode: 'fixed',
          description: `等待 ${duration / 1000} 秒`,
          duration,
        },
      });
      setShowAddWait(false);
    } catch (error) {
      console.error('Add step failed:', error);
    }
  };

  if (isLoading) {
    return <div className="p-6 text-center text-gray-500">加载中...</div>;
  }

  if (!recording) {
    return <div className="p-6 text-center text-gray-500">录制不存在</div>;
  }

  return (
    <div className="p-6">
      {/* 头部 */}
      <div className="flex items-center gap-4 mb-6">
        <Link
          to={`/recordings/${recordingId}`}
          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <ArrowLeft size={20} />
        </Link>
        <div className="flex-1">
          <h1 className="text-2xl font-bold text-gray-900">编辑步骤</h1>
          <p className="text-gray-500">{recording.name}</p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowAddWait(true)}
            className="btn btn-secondary flex items-center gap-2"
          >
            <Plus size={16} />
            添加等待
          </button>
        </div>
      </div>

      {/* 说明 */}
      <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <p className="text-sm text-blue-700">
          点击步骤可以编辑其属性。你可以将步骤设置为 AI 决策模式，让 AI 根据屏幕内容做出选择。
        </p>
      </div>

      {/* 步骤列表 */}
      <div className="space-y-2">
        {recording.steps.map((step) => (
          <StepItem
            key={step.id}
            step={step}
            onClick={() => setEditingStep(step)}
            onEdit={() => setEditingStep(step)}
            onDelete={() => handleDeleteStep(step.id)}
          />
        ))}
      </div>

      {recording.steps.length === 0 && (
        <div className="text-center py-12 text-gray-500">暂无步骤</div>
      )}

      {/* 步骤编辑器 */}
      {editingStep && (
        <StepEditor
          step={editingStep}
          onSave={handleUpdateStep}
          onClose={() => setEditingStep(null)}
        />
      )}

      {/* 添加等待步骤弹窗 */}
      {showAddWait && (
        <AddWaitModal
          onAdd={handleAddWaitStep}
          onClose={() => setShowAddWait(false)}
        />
      )}
    </div>
  );
}

function AddWaitModal({
  onAdd,
  onClose,
}: {
  onAdd: (duration: number) => void;
  onClose: () => void;
}) {
  const [duration, setDuration] = useState(3000);

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl shadow-xl w-[400px] p-6">
        <h2 className="text-lg font-semibold mb-4">添加等待步骤</h2>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            等待时间 (毫秒)
          </label>
          <input
            type="number"
            value={duration}
            onChange={(e) => setDuration(Number(e.target.value))}
            min={100}
            step={100}
            className="input"
          />
          <p className="text-xs text-gray-500 mt-1">
            {(duration / 1000).toFixed(1)} 秒
          </p>
        </div>
        <div className="flex justify-end gap-3 mt-6">
          <button onClick={onClose} className="btn btn-secondary">
            取消
          </button>
          <button
            onClick={() => onAdd(duration)}
            className="btn btn-primary"
          >
            添加
          </button>
        </div>
      </div>
    </div>
  );
}

import { useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  Play,
  Video,
  Square,
  Trash2,
  Edit,
  MoreVertical,
  Calendar,
} from 'lucide-react';
import { useProject, useProjectRecordings } from '../hooks/useProjects';
import { useDeleteRecording } from '../hooks/useRecordings';
import { useRecorderStatus, useStopRecording } from '../hooks/useRecorder';
import { useStartPlayback } from '../hooks/usePlayback';
import WindowSelector from '../components/WindowSelector';

export default function ProjectDetailPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const { data: project, isLoading: projectLoading } = useProject(projectId!);
  const { data: recordings, isLoading: recordingsLoading } = useProjectRecordings(projectId!);
  const { data: recorderStatus } = useRecorderStatus();
  const stopRecording = useStopRecording();
  const deleteRecording = useDeleteRecording();
  const startPlayback = useStartPlayback();
  const [showWindowSelector, setShowWindowSelector] = useState(false);

  const isRecording = recorderStatus?.is_recording && recorderStatus.project_id === projectId;

  const handleStopRecording = async () => {
    try {
      const recording = await stopRecording.mutateAsync();
      if (recording) {
        navigate(`/recordings/${recording.id}`);
      }
    } catch (error) {
      console.error('Stop recording failed:', error);
    }
  };

  const handlePlayRecording = async (recordingId: string, e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();

    try {
      await startPlayback.mutateAsync({ recordingId });
    } catch (error) {
      console.error('Start playback failed:', error);
    }
  };

  const handleDeleteRecording = async (recordingId: string, e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();

    if (!confirm('确定要删除此录制吗？')) return;

    try {
      await deleteRecording.mutateAsync(recordingId);
    } catch (error) {
      console.error('Delete recording failed:', error);
    }
  };

  if (projectLoading) {
    return (
      <div className="p-6 text-center text-gray-500">加载中...</div>
    );
  }

  if (!project) {
    return (
      <div className="p-6 text-center text-gray-500">项目不存在</div>
    );
  }

  return (
    <div className="p-6">
      {/* 头部 */}
      <div className="flex items-center gap-4 mb-6">
        <Link
          to="/"
          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <ArrowLeft size={20} />
        </Link>
        <div className="flex-1">
          <h1 className="text-2xl font-bold text-gray-900">{project.name}</h1>
          {project.description && (
            <p className="text-gray-500">{project.description}</p>
          )}
        </div>
        <div className="flex items-center gap-2">
          {isRecording ? (
            <button
              onClick={handleStopRecording}
              disabled={stopRecording.isPending}
              className="btn bg-red-600 text-white hover:bg-red-700 flex items-center gap-2"
            >
              <Square size={16} />
              {stopRecording.isPending ? '停止中...' : '停止录制'}
            </button>
          ) : (
            <button
              onClick={() => setShowWindowSelector(true)}
              className="btn btn-primary flex items-center gap-2"
            >
              <Video size={16} />
              开始录制
            </button>
          )}
        </div>
      </div>

      {/* 录制状态 */}
      {isRecording && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-center gap-2 text-red-600">
            <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
            <span className="font-medium">正在录制中...</span>
            <span className="text-red-500">
              已记录 {recorderStatus?.step_count || 0} 步
            </span>
          </div>
        </div>
      )}

      {/* 录制列表 */}
      <div className="mb-4">
        <h2 className="text-lg font-semibold text-gray-900">录制列表</h2>
      </div>

      {recordingsLoading ? (
        <div className="text-center text-gray-500 py-12">加载中...</div>
      ) : recordings?.length === 0 ? (
        <div className="text-center py-12">
          <Video size={48} className="mx-auto text-gray-300 mb-4" />
          <p className="text-gray-500">暂无录制</p>
          <button
            onClick={() => setShowWindowSelector(true)}
            className="mt-4 text-primary-600 hover:underline"
          >
            开始第一次录制
          </button>
        </div>
      ) : (
        <div className="space-y-3">
          {recordings?.map((recording) => (
            <Link
              key={recording.id}
              to={`/recordings/${recording.id}`}
              className="block card hover:shadow-md transition-shadow group"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-green-100 flex items-center justify-center">
                    <Video size={20} className="text-green-600" />
                  </div>
                  <div>
                    <h3 className="font-medium text-gray-900">{recording.name}</h3>
                    <div className="flex items-center gap-3 text-sm text-gray-500">
                      <span>{recording.steps.length} 步</span>
                      {recording.target_window && (
                        <span>窗口: {recording.target_window.title}</span>
                      )}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <div className="flex items-center gap-1 text-xs text-gray-400">
                    <Calendar size={12} />
                    {new Date(recording.created_at).toLocaleDateString()}
                  </div>
                  <button
                    onClick={(e) => handlePlayRecording(recording.id, e)}
                    className="p-2 rounded hover:bg-green-100 text-green-600 transition-colors"
                    title="执行"
                  >
                    <Play size={16} />
                  </button>
                  <Link
                    to={`/recordings/${recording.id}/edit`}
                    onClick={(e) => e.stopPropagation()}
                    className="p-2 rounded hover:bg-gray-100 transition-colors"
                    title="编辑"
                  >
                    <Edit size={16} />
                  </Link>
                  <button
                    onClick={(e) => handleDeleteRecording(recording.id, e)}
                    className="p-2 rounded hover:bg-red-100 text-red-600 transition-colors"
                    title="删除"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}

      {/* 窗口选择器 */}
      {showWindowSelector && (
        <WindowSelector
          projectId={projectId!}
          onClose={() => setShowWindowSelector(false)}
        />
      )}
    </div>
  );
}

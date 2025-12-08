import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, Play, Pause, Square, Edit, Clock } from 'lucide-react';
import { useRecording } from '../hooks/useRecordings';
import {
  usePlaybackStatus,
  useStartPlayback,
  usePausePlayback,
  useResumePlayback,
  useStopPlayback,
  usePlaybackLogs,
} from '../hooks/usePlayback';
import StepItem from '../components/StepItem';

export default function RecordingPage() {
  const { recordingId } = useParams<{ recordingId: string }>();
  const { data: recording, isLoading } = useRecording(recordingId!);
  const { data: playbackStatus } = usePlaybackStatus();
  const { data: logs } = usePlaybackLogs();
  const startPlayback = useStartPlayback();
  const pausePlayback = usePausePlayback();
  const resumePlayback = useResumePlayback();
  const stopPlayback = useStopPlayback();

  const isPlaying = playbackStatus?.status === 'playing' && playbackStatus.recording_id === recordingId;
  const isPaused = playbackStatus?.status === 'paused' && playbackStatus.recording_id === recordingId;
  const isRunning = isPlaying || isPaused;

  const handlePlay = async () => {
    try {
      await startPlayback.mutateAsync({ recordingId: recordingId! });
    } catch (error) {
      console.error('Start playback failed:', error);
    }
  };

  const handlePause = async () => {
    try {
      await pausePlayback.mutateAsync();
    } catch (error) {
      console.error('Pause playback failed:', error);
    }
  };

  const handleResume = async () => {
    try {
      await resumePlayback.mutateAsync();
    } catch (error) {
      console.error('Resume playback failed:', error);
    }
  };

  const handleStop = async () => {
    try {
      await stopPlayback.mutateAsync();
    } catch (error) {
      console.error('Stop playback failed:', error);
    }
  };

  if (isLoading) {
    return <div className="p-6 text-center text-gray-500">加载中...</div>;
  }

  if (!recording) {
    return <div className="p-6 text-center text-gray-500">录制不存在</div>;
  }

  const currentStepIndex = playbackStatus?.current_step || 0;

  return (
    <div className="p-6">
      {/* 头部 */}
      <div className="flex items-center gap-4 mb-6">
        <Link
          to={`/projects/${recording.project_id}`}
          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <ArrowLeft size={20} />
        </Link>
        <div className="flex-1">
          <h1 className="text-2xl font-bold text-gray-900">{recording.name}</h1>
          <p className="text-gray-500">
            {recording.steps.length} 个步骤
            {recording.target_window && ` · ${recording.target_window.title}`}
          </p>
        </div>
        <div className="flex items-center gap-2">
          {isRunning ? (
            <>
              {isPlaying ? (
                <button
                  onClick={handlePause}
                  className="btn btn-secondary flex items-center gap-2"
                >
                  <Pause size={16} />
                  暂停
                </button>
              ) : (
                <button
                  onClick={handleResume}
                  className="btn btn-primary flex items-center gap-2"
                >
                  <Play size={16} />
                  继续
                </button>
              )}
              <button
                onClick={handleStop}
                className="btn bg-red-600 text-white hover:bg-red-700 flex items-center gap-2"
              >
                <Square size={16} />
                停止
              </button>
            </>
          ) : (
            <>
              <button
                onClick={handlePlay}
                disabled={startPlayback.isPending}
                className="btn btn-primary flex items-center gap-2"
              >
                <Play size={16} />
                {startPlayback.isPending ? '启动中...' : '执行'}
              </button>
              <Link
                to={`/recordings/${recordingId}/edit`}
                className="btn btn-secondary flex items-center gap-2"
              >
                <Edit size={16} />
                编辑
              </Link>
            </>
          )}
        </div>
      </div>

      {/* 执行状态 */}
      {isRunning && (
        <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-green-600">
              {isPlaying && (
                <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
              )}
              <span className="font-medium">
                {isPlaying ? '正在执行...' : '已暂停'}
              </span>
              <span className="text-green-500">
                {currentStepIndex}/{recording.steps.length} 步
              </span>
            </div>
            <div className="flex items-center gap-1 text-green-600">
              <Clock size={14} />
              <span>{Math.floor((playbackStatus?.duration || 0) / 1000)}s</span>
            </div>
          </div>
          {/* 进度条 */}
          <div className="mt-2 h-2 bg-green-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-green-500 transition-all duration-300"
              style={{
                width: `${(currentStepIndex / recording.steps.length) * 100}%`,
              }}
            />
          </div>
        </div>
      )}

      {/* 步骤列表 */}
      <div className="space-y-2">
        {recording.steps.map((step, index) => (
          <StepItem
            key={step.id}
            step={step}
            isActive={isRunning && index === currentStepIndex}
          />
        ))}
      </div>

      {recording.steps.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          暂无步骤
        </div>
      )}

      {/* 执行日志 */}
      {logs && logs.length > 0 && (
        <div className="mt-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-3">执行日志</h2>
          <div className="card max-h-60 overflow-auto">
            <div className="space-y-1 text-sm font-mono">
              {logs.map((log, index) => (
                <div
                  key={index}
                  className={`flex items-center gap-2 ${
                    log.status === 'success' ? 'text-green-600' : 'text-red-600'
                  }`}
                >
                  <span className="text-gray-400 w-16">
                    {new Date(log.timestamp).toLocaleTimeString()}
                  </span>
                  <span className={`w-16 ${
                    log.status === 'success' ? 'text-green-600' : 'text-red-600'
                  }`}>
                    [{log.status}]
                  </span>
                  <span className="text-gray-600">{log.message || log.step_id}</span>
                  <span className="text-gray-400">{log.duration}ms</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

import { Outlet, Link, useLocation } from 'react-router-dom';
import { Home, FolderOpen, Settings, Circle } from 'lucide-react';
import { useRecorderStatus } from '../hooks/useRecorder';
import { usePlaybackStatus } from '../hooks/usePlayback';
import clsx from 'clsx';

export default function Layout() {
  const location = useLocation();
  const { data: recorderStatus } = useRecorderStatus();
  const { data: playbackStatus } = usePlaybackStatus();

  const isRecording = recorderStatus?.is_recording;
  const isPlaying = playbackStatus?.status === 'playing';

  return (
    <div className="flex h-screen bg-gray-100">
      {/* 侧边栏 */}
      <aside className="w-64 bg-white shadow-md">
        <div className="p-4 border-b">
          <h1 className="text-xl font-bold text-primary-600">TeachPlay</h1>
          <p className="text-sm text-gray-500">游戏自动化系统</p>
        </div>

        <nav className="p-4">
          <ul className="space-y-2">
            <li>
              <Link
                to="/"
                className={clsx(
                  'flex items-center gap-2 px-3 py-2 rounded-lg transition-colors',
                  location.pathname === '/'
                    ? 'bg-primary-100 text-primary-700'
                    : 'text-gray-600 hover:bg-gray-100'
                )}
              >
                <Home size={20} />
                项目列表
              </Link>
            </li>
          </ul>
        </nav>

        {/* 状态指示器 */}
        <div className="absolute bottom-0 left-0 w-64 p-4 border-t bg-white">
          {isRecording && (
            <div className="flex items-center gap-2 text-red-600">
              <Circle size={12} className="fill-current animate-pulse" />
              <span className="text-sm">录制中...</span>
              <span className="text-xs text-gray-500">
                {recorderStatus?.step_count} 步
              </span>
            </div>
          )}
          {isPlaying && (
            <div className="flex items-center gap-2 text-green-600">
              <Circle size={12} className="fill-current animate-pulse" />
              <span className="text-sm">执行中...</span>
              <span className="text-xs text-gray-500">
                {playbackStatus?.current_step}/{playbackStatus?.total_steps}
              </span>
            </div>
          )}
          {!isRecording && !isPlaying && (
            <div className="flex items-center gap-2 text-gray-400">
              <Circle size={12} />
              <span className="text-sm">空闲</span>
            </div>
          )}
        </div>
      </aside>

      {/* 主内容区 */}
      <main className="flex-1 overflow-auto">
        <Outlet />
      </main>
    </div>
  );
}

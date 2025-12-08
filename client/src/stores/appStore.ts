import { create } from 'zustand';
import type { RecorderStatus, PlaybackStatus } from '../types';

interface AppState {
  // 录制状态
  recorderStatus: RecorderStatus | null;
  setRecorderStatus: (status: RecorderStatus | null) => void;

  // 回放状态
  playbackStatus: PlaybackStatus | null;
  setPlaybackStatus: (status: PlaybackStatus | null) => void;

  // UI状态
  selectedProjectId: string | null;
  setSelectedProjectId: (id: string | null) => void;

  // 窗口选择对话框
  isWindowSelectorOpen: boolean;
  openWindowSelector: () => void;
  closeWindowSelector: () => void;
}

export const useAppStore = create<AppState>((set) => ({
  // 录制状态
  recorderStatus: null,
  setRecorderStatus: (status) => set({ recorderStatus: status }),

  // 回放状态
  playbackStatus: null,
  setPlaybackStatus: (status) => set({ playbackStatus: status }),

  // UI状态
  selectedProjectId: null,
  setSelectedProjectId: (id) => set({ selectedProjectId: id }),

  // 窗口选择对话框
  isWindowSelectorOpen: false,
  openWindowSelector: () => set({ isWindowSelectorOpen: true }),
  closeWindowSelector: () => set({ isWindowSelectorOpen: false }),
}));

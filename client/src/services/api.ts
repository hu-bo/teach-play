const API_BASE = 'http://localhost:8000/api';

async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE}${endpoint}`;

  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || 'Request failed');
  }

  return response.json();
}

// 项目API
export const projectsApi = {
  list: () => request<Project[]>('/projects'),

  get: (id: string) => request<Project>(`/projects/${id}`),

  create: (data: ProjectCreate) =>
    request<Project>('/projects', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  update: (id: string, data: ProjectUpdate) =>
    request<Project>(`/projects/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  delete: (id: string) =>
    request<void>(`/projects/${id}`, { method: 'DELETE' }),

  getRecordings: (id: string) =>
    request<Recording[]>(`/projects/${id}/recordings`),
};

// 录制API
export const recordingsApi = {
  list: (projectId?: string) => {
    const params = projectId ? `?project_id=${projectId}` : '';
    return request<Recording[]>(`/recordings${params}`);
  },

  get: (id: string) => request<Recording>(`/recordings/${id}`),

  create: (data: RecordingCreate) =>
    request<Recording>('/recordings', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  update: (id: string, data: RecordingUpdate) =>
    request<Recording>(`/recordings/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  delete: (id: string) =>
    request<void>(`/recordings/${id}`, { method: 'DELETE' }),

  // 步骤
  getSteps: (recordingId: string) =>
    request<Step[]>(`/recordings/${recordingId}/steps`),

  addStep: (recordingId: string, step: StepCreate) =>
    request<Step>(`/recordings/${recordingId}/steps`, {
      method: 'POST',
      body: JSON.stringify(step),
    }),

  updateStep: (recordingId: string, stepId: string, step: StepUpdate) =>
    request<Step>(`/recordings/${recordingId}/steps/${stepId}`, {
      method: 'PUT',
      body: JSON.stringify(step),
    }),

  deleteStep: (recordingId: string, stepId: string) =>
    request<void>(`/recordings/${recordingId}/steps/${stepId}`, {
      method: 'DELETE',
    }),

  reorderSteps: (recordingId: string, stepIds: string[]) =>
    request<Step[]>(`/recordings/${recordingId}/steps/reorder`, {
      method: 'PUT',
      body: JSON.stringify(stepIds),
    }),
};

// 录制控制API
export const recorderApi = {
  listWindows: () => request<WindowInfo[]>('/record/windows'),

  start: (projectId: string, windowId: string, name?: string) =>
    request<Recording>('/record/start', {
      method: 'POST',
      body: JSON.stringify({ project_id: projectId, window_id: windowId, name }),
    }),

  stop: () => request<Recording>('/record/stop', { method: 'POST' }),

  getStatus: () => request<RecorderStatus>('/record/status'),
};

// 回放控制API
export const playbackApi = {
  start: (recordingId: string, startIndex = 0) =>
    request<PlaybackStatus>('/playback/start', {
      method: 'POST',
      body: JSON.stringify({ recording_id: recordingId, start_index: startIndex }),
    }),

  pause: () => request<PlaybackStatus>('/playback/pause', { method: 'POST' }),

  resume: () => request<PlaybackStatus>('/playback/resume', { method: 'POST' }),

  stop: () => request<PlaybackStatus>('/playback/stop', { method: 'POST' }),

  getStatus: () => request<PlaybackStatus>('/playback/status'),

  getLogs: () => request<StepLog[]>('/playback/logs'),
};

// 文件API
export const filesApi = {
  upload: async (file: File, path?: string) => {
    const formData = new FormData();
    formData.append('file', file);
    if (path) formData.append('path', path);

    const response = await fetch(`${API_BASE}/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error('Upload failed');
    }

    return response.json();
  },

  getUrl: (path: string) => `${API_BASE}/files/${path}`,
};

// 类型导入
import type {
  Project,
  ProjectCreate,
  ProjectUpdate,
  Recording,
  RecordingCreate,
  RecordingUpdate,
  Step,
  StepCreate,
  StepUpdate,
  WindowInfo,
  RecorderStatus,
  PlaybackStatus,
  StepLog,
} from '../types';

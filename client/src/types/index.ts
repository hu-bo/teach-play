// 基础类型

export interface Position {
  x: number;
  y: number;
}

export interface Region {
  x: number;
  y: number;
  width: number;
  height: number;
}

// 项目

export interface Project {
  id: string;
  name: string;
  description: string;
  created_at: string;
  updated_at: string;
  recordings: string[];
}

export interface ProjectCreate {
  name: string;
  description?: string;
}

export interface ProjectUpdate {
  name?: string;
  description?: string;
}

// 录制

export interface TargetWindow {
  title: string;
  process_name: string;
  rect: Region;
}

export interface Recording {
  id: string;
  name: string;
  project_id: string;
  created_at: string;
  target_window?: TargetWindow;
  steps: Step[];
}

export interface RecordingCreate {
  name: string;
  project_id: string;
}

export interface RecordingUpdate {
  name?: string;
}

// 步骤

export type StepType = 'click' | 'scroll' | 'drag' | 'input' | 'key' | 'wait' | 'file_select';
export type StepMode = 'fixed' | 'smart' | 'ai_decision';

export interface AIConfig {
  prompt: string;
  options: Array<{
    label: string;
    region: Region;
    description?: string;
  }>;
}

export interface WaitCondition {
  type: 'text_appear' | 'text_disappear' | 'image_match';
  value: string;
  region?: Region;
  threshold?: number;
}

export interface Step {
  id: string;
  index: number;
  type: StepType;
  mode: StepMode;
  position?: Position;
  text?: string;
  screenshot?: string;
  description: string;
  timestamp: number;

  // click
  button?: string;

  // scroll
  direction?: string;
  amount?: number;

  // drag
  from?: Position;
  to?: Position;

  // input
  input_text?: string;

  // key
  key?: string;

  // file_select
  file_path?: string;

  // wait
  duration?: number;
  condition?: WaitCondition;
  timeout?: number;

  // ai_decision
  ai_config?: AIConfig;
}

export interface StepCreate {
  type: StepType;
  mode?: StepMode;
  position?: Position;
  text?: string;
  description?: string;
  [key: string]: unknown;
}

export interface StepUpdate {
  type?: StepType;
  mode?: StepMode;
  position?: Position;
  text?: string;
  description?: string;
  ai_config?: AIConfig;
  [key: string]: unknown;
}

// 窗口

export interface WindowInfo {
  window_id: string;
  title: string;
  process_name: string;
  rect: Region;
  thumbnail?: string;
}

// 录制状态

export interface RecorderStatus {
  is_recording: boolean;
  recording_id?: string;
  project_id?: string;
  step_count: number;
  duration: number;
}

// 回放状态

export type PlaybackStatusType = 'idle' | 'playing' | 'paused' | 'stopped' | 'completed' | 'error';

export interface PlaybackStatus {
  status: PlaybackStatusType;
  recording_id?: string;
  current_step: number;
  total_steps: number;
  duration: number;
  error?: string;
}

export interface StepLog {
  step_id: string;
  status: string;
  message: string;
  duration: number;
  timestamp: number;
}

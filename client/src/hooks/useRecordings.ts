import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { recordingsApi } from '../services/api';
import type { RecordingCreate, RecordingUpdate, StepCreate, StepUpdate } from '../types';

export function useRecordings(projectId?: string) {
  return useQuery({
    queryKey: ['recordings', { projectId }],
    queryFn: () => recordingsApi.list(projectId),
  });
}

export function useRecording(id: string) {
  return useQuery({
    queryKey: ['recordings', id],
    queryFn: () => recordingsApi.get(id),
    enabled: !!id,
  });
}

export function useCreateRecording() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: RecordingCreate) => recordingsApi.create(data),
    onSuccess: (_, { project_id }) => {
      queryClient.invalidateQueries({ queryKey: ['recordings'] });
      queryClient.invalidateQueries({ queryKey: ['projects', project_id, 'recordings'] });
    },
  });
}

export function useUpdateRecording() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: RecordingUpdate }) =>
      recordingsApi.update(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['recordings'] });
      queryClient.invalidateQueries({ queryKey: ['recordings', id] });
    },
  });
}

export function useDeleteRecording() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => recordingsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['recordings'] });
    },
  });
}

// 步骤操作

export function useSteps(recordingId: string) {
  return useQuery({
    queryKey: ['recordings', recordingId, 'steps'],
    queryFn: () => recordingsApi.getSteps(recordingId),
    enabled: !!recordingId,
  });
}

export function useAddStep() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ recordingId, step }: { recordingId: string; step: StepCreate }) =>
      recordingsApi.addStep(recordingId, step),
    onSuccess: (_, { recordingId }) => {
      queryClient.invalidateQueries({ queryKey: ['recordings', recordingId] });
      queryClient.invalidateQueries({ queryKey: ['recordings', recordingId, 'steps'] });
    },
  });
}

export function useUpdateStep() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      recordingId,
      stepId,
      step,
    }: {
      recordingId: string;
      stepId: string;
      step: StepUpdate;
    }) => recordingsApi.updateStep(recordingId, stepId, step),
    onSuccess: (_, { recordingId }) => {
      queryClient.invalidateQueries({ queryKey: ['recordings', recordingId] });
      queryClient.invalidateQueries({ queryKey: ['recordings', recordingId, 'steps'] });
    },
  });
}

export function useDeleteStep() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ recordingId, stepId }: { recordingId: string; stepId: string }) =>
      recordingsApi.deleteStep(recordingId, stepId),
    onSuccess: (_, { recordingId }) => {
      queryClient.invalidateQueries({ queryKey: ['recordings', recordingId] });
      queryClient.invalidateQueries({ queryKey: ['recordings', recordingId, 'steps'] });
    },
  });
}

export function useReorderSteps() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ recordingId, stepIds }: { recordingId: string; stepIds: string[] }) =>
      recordingsApi.reorderSteps(recordingId, stepIds),
    onSuccess: (_, { recordingId }) => {
      queryClient.invalidateQueries({ queryKey: ['recordings', recordingId] });
      queryClient.invalidateQueries({ queryKey: ['recordings', recordingId, 'steps'] });
    },
  });
}

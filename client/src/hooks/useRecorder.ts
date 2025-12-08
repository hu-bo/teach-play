import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { recorderApi } from '../services/api';
import { useAppStore } from '../stores/appStore';

export function useWindows() {
  return useQuery({
    queryKey: ['windows'],
    queryFn: recorderApi.listWindows,
  });
}

export function useRecorderStatus() {
  const setRecorderStatus = useAppStore((state) => state.setRecorderStatus);

  return useQuery({
    queryKey: ['recorder', 'status'],
    queryFn: async () => {
      const status = await recorderApi.getStatus();
      setRecorderStatus(status);
      return status;
    },
    refetchInterval: 1000, // 每秒刷新一次
  });
}

export function useStartRecording() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      projectId,
      windowId,
      name,
    }: {
      projectId: string;
      windowId: string;
      name?: string;
    }) => recorderApi.start(projectId, windowId, name),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['recorder', 'status'] });
      queryClient.invalidateQueries({ queryKey: ['recordings'] });
    },
  });
}

export function useStopRecording() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => recorderApi.stop(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['recorder', 'status'] });
      queryClient.invalidateQueries({ queryKey: ['recordings'] });
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    },
  });
}

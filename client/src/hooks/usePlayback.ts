import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { playbackApi } from '../services/api';
import { useAppStore } from '../stores/appStore';

export function usePlaybackStatus() {
  const setPlaybackStatus = useAppStore((state) => state.setPlaybackStatus);

  return useQuery({
    queryKey: ['playback', 'status'],
    queryFn: async () => {
      const status = await playbackApi.getStatus();
      setPlaybackStatus(status);
      return status;
    },
    refetchInterval: 1000,
  });
}

export function usePlaybackLogs() {
  return useQuery({
    queryKey: ['playback', 'logs'],
    queryFn: playbackApi.getLogs,
    refetchInterval: 1000,
  });
}

export function useStartPlayback() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ recordingId, startIndex = 0 }: { recordingId: string; startIndex?: number }) =>
      playbackApi.start(recordingId, startIndex),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['playback'] });
    },
  });
}

export function usePausePlayback() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => playbackApi.pause(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['playback', 'status'] });
    },
  });
}

export function useResumePlayback() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => playbackApi.resume(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['playback', 'status'] });
    },
  });
}

export function useStopPlayback() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => playbackApi.stop(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['playback', 'status'] });
    },
  });
}

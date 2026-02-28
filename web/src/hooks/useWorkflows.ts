import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { workflowsApi, dashboardApi } from "@/lib/api";
import type { CreateWorkflowRequest } from "@/types";

export function useWorkflows(page = 1) {
  return useQuery({
    queryKey: ["workflows", page],
    queryFn: () => workflowsApi.list(page),
    refetchInterval: 10000, // poll every 10s as fallback
  });
}

export function useWorkflow(id: string | undefined) {
  return useQuery({
    queryKey: ["workflow", id],
    queryFn: () => workflowsApi.get(id!),
    enabled: !!id,
    refetchInterval: (query) =>
      query.state.data?.status === "RUNNING" ? 3000 : false,
  });
}

export function useCreateWorkflow() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: CreateWorkflowRequest) => workflowsApi.create(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["workflows"] }),
  });
}

export function useApproveWorkflow() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, phase }: { id: string; phase: string }) =>
      workflowsApi.approve(id, phase),
    onSuccess: (_, vars) => {
      qc.invalidateQueries({ queryKey: ["workflow", vars.id] });
      qc.invalidateQueries({ queryKey: ["workflows"] });
    },
  });
}

export function useDashboardStats() {
  return useQuery({
    queryKey: ["dashboard-stats"],
    queryFn: dashboardApi.getStats,
    refetchInterval: 30000,
  });
}

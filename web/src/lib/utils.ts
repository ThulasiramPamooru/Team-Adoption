import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";
import { formatDistanceToNow, format } from "date-fns";
import type { StepStatus, WorkflowStatus } from "@/types";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(date: string) {
  return format(new Date(date), "MMM d, yyyy HH:mm");
}

export function timeAgo(date: string) {
  return formatDistanceToNow(new Date(date), { addSuffix: true });
}

export function formatDuration(ms: number): string {
  if (ms < 1000) return `${ms}ms`;
  if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
  return `${Math.floor(ms / 60000)}m ${Math.floor((ms % 60000) / 1000)}s`;
}

export const STEP_STATUS_COLORS: Record<StepStatus, string> = {
  PENDING: "text-muted-foreground",
  IN_PROGRESS: "text-blue-500",
  PASSED: "text-green-500",
  BLOCKED: "text-yellow-500",
  FAILED: "text-destructive",
  SKIPPED: "text-muted-foreground",
};

export const WORKFLOW_STATUS_COLORS: Record<WorkflowStatus, string> = {
  PENDING: "bg-muted text-muted-foreground",
  RUNNING: "bg-blue-100 text-blue-700",
  COMPLETED: "bg-green-100 text-green-700",
  FAILED: "bg-red-100 text-red-700",
  BLOCKED: "bg-yellow-100 text-yellow-700",
  AWAITING_APPROVAL: "bg-orange-100 text-orange-700",
};

export const SEVERITY_COLORS = {
  LOW: "bg-blue-100 text-blue-700",
  MEDIUM: "bg-yellow-100 text-yellow-700",
  HIGH: "bg-orange-100 text-orange-700",
  CRITICAL: "bg-red-100 text-red-700",
};

import {
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Clock,
  Loader2,
  MinusCircle,
} from "lucide-react";
import { cn, STEP_STATUS_COLORS, formatDuration } from "@/lib/utils";
import type { WorkflowStep, WorkflowPhase } from "@/types";
import { PHASE_LABELS, PHASE_DESCRIPTIONS } from "@/types";

interface PhaseStepProps {
  step: WorkflowStep;
  index: number;
  isLast: boolean;
  onApprove?: (phase: WorkflowPhase) => void;
  canApprove?: boolean;
}

const StatusIcon = ({ status }: { status: WorkflowStep["status"] }) => {
  const cls = "w-5 h-5";
  switch (status) {
    case "PASSED": return <CheckCircle2 className={cn(cls, "text-green-500")} />;
    case "FAILED": return <XCircle className={cn(cls, "text-red-500")} />;
    case "BLOCKED": return <AlertTriangle className={cn(cls, "text-yellow-500")} />;
    case "IN_PROGRESS": return <Loader2 className={cn(cls, "text-blue-500 animate-spin")} />;
    case "SKIPPED": return <MinusCircle className={cn(cls, "text-muted-foreground")} />;
    default: return <Clock className={cn(cls, "text-muted-foreground")} />;
  }
};

export function PhaseStep({ step, index, isLast, onApprove, canApprove }: PhaseStepProps) {
  return (
    <div className="flex gap-4">
      {/* Timeline line */}
      <div className="flex flex-col items-center">
        <div className={cn(
          "w-9 h-9 rounded-full border-2 flex items-center justify-center bg-background z-10",
          step.status === "PASSED" && "border-green-500",
          step.status === "FAILED" && "border-red-500",
          step.status === "BLOCKED" && "border-yellow-500",
          step.status === "IN_PROGRESS" && "border-blue-500",
          step.status === "PENDING" && "border-muted",
        )}>
          <StatusIcon status={step.status} />
        </div>
        {!isLast && <div className="w-0.5 flex-1 bg-border mt-1" />}
      </div>

      {/* Content */}
      <div className={cn("pb-6 flex-1", isLast && "pb-0")}>
        <div className="flex items-start justify-between gap-2">
          <div>
            <p className="font-medium text-sm">
              <span className="text-muted-foreground mr-1">Phase {index + 1}:</span>
              {PHASE_LABELS[step.phase]}
            </p>
            <p className="text-xs text-muted-foreground mt-0.5">
              {PHASE_DESCRIPTIONS[step.phase]}
            </p>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            {step.duration && (
              <span className="text-xs text-muted-foreground">
                {formatDuration(step.duration)}
              </span>
            )}
            <span className={cn("text-xs font-medium", STEP_STATUS_COLORS[step.status])}>
              {step.status}
            </span>
          </div>
        </div>

        {/* Output log */}
        {step.output && (
          <pre className="mt-2 text-xs bg-muted rounded p-3 overflow-x-auto max-h-40 overflow-y-auto whitespace-pre-wrap">
            {step.output}
          </pre>
        )}

        {/* Artifacts */}
        {step.artifacts && Object.keys(step.artifacts).length > 0 && (
          <div className="mt-2 flex flex-wrap gap-2">
            {Object.entries(step.artifacts).map(([key, url]) => (
              <a
                key={key}
                href={url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs text-blue-600 underline hover:text-blue-800"
              >
                {key}
              </a>
            ))}
          </div>
        )}

        {/* Approve button for BLOCKED steps */}
        {step.status === "BLOCKED" && canApprove && onApprove && (
          <button
            onClick={() => onApprove(step.phase)}
            className="mt-3 px-3 py-1.5 text-xs font-medium bg-yellow-500 text-white rounded hover:bg-yellow-600 transition-colors"
          >
            Approve & Continue
          </button>
        )}
      </div>
    </div>
  );
}

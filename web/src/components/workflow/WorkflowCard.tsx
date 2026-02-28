import { Link } from "react-router-dom";
import { GitBranch, ExternalLink, Clock } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { cn, timeAgo, WORKFLOW_STATUS_COLORS } from "@/lib/utils";
import { PHASE_ORDER, PHASE_LABELS } from "@/types";
import type { Workflow } from "@/types";

interface WorkflowCardProps {
  workflow: Workflow;
}

function getProgress(workflow: Workflow): number {
  const passed = workflow.steps.filter((s) => s.status === "PASSED").length;
  return Math.round((passed / PHASE_ORDER.length) * 100);
}

export function WorkflowCard({ workflow }: WorkflowCardProps) {
  const progress = getProgress(workflow);

  return (
    <Link to={`/workflows/${workflow.id}`}>
      <Card className="hover:shadow-md transition-shadow cursor-pointer">
        <CardContent className="p-5">
          <div className="flex items-start justify-between gap-3">
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-xs font-mono font-semibold text-flowguard-600 bg-flowguard-50 px-2 py-0.5 rounded">
                  {workflow.task_id}
                </span>
                <Badge className={cn("text-xs", WORKFLOW_STATUS_COLORS[workflow.status])}>
                  {workflow.status}
                </Badge>
              </div>
              <p className="font-medium text-sm truncate">{workflow.title}</p>
              <p className="text-xs text-muted-foreground mt-0.5">
                App: <span className="font-medium">{workflow.target_app}</span>
              </p>
            </div>

            {/* External links */}
            <div className="flex gap-1 shrink-0">
              {workflow.github_pr_url && (
                <a
                  href={workflow.github_pr_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  onClick={(e) => e.stopPropagation()}
                  className="p-1 text-muted-foreground hover:text-foreground"
                  title="GitHub PR"
                >
                  <GitBranch className="w-3.5 h-3.5" />
                </a>
              )}
              {workflow.jira_url && (
                <a
                  href={workflow.jira_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  onClick={(e) => e.stopPropagation()}
                  className="p-1 text-muted-foreground hover:text-foreground"
                  title="Jira Issue"
                >
                  <ExternalLink className="w-3.5 h-3.5" />
                </a>
              )}
            </div>
          </div>

          {/* Progress bar */}
          <div className="mt-4">
            <div className="flex justify-between text-xs text-muted-foreground mb-1.5">
              <span>
                {workflow.current_phase
                  ? PHASE_LABELS[workflow.current_phase]
                  : "Not started"}
              </span>
              <span>{progress}%</span>
            </div>
            <Progress value={progress} className="h-1.5" />
          </div>

          {/* Footer */}
          <div className="flex items-center gap-1 mt-3 text-xs text-muted-foreground">
            <Clock className="w-3 h-3" />
            <span>{timeAgo(workflow.updated_at)}</span>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}

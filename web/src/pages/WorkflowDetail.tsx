import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { ArrowLeft, GitBranch, ExternalLink, RefreshCw } from "lucide-react";
import { useAuth0 } from "@auth0/auth0-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { PhaseStep } from "@/components/workflow/PhaseStep";
import { useWorkflow, useApproveWorkflow } from "@/hooks/useWorkflows";
import { useWorkflowWebSocket } from "@/hooks/useWebSocket";
import { cn, WORKFLOW_STATUS_COLORS, formatDate } from "@/lib/utils";
import type { WorkflowPhase } from "@/types";
import { PHASE_ORDER } from "@/types";

export function WorkflowDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { data: workflow, isLoading, refetch } = useWorkflow(id);
  const { mutateAsync: approve, isPending: isApproving } = useApproveWorkflow();
  const { getAccessTokenSilently } = useAuth0();
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    getAccessTokenSilently().then(setToken).catch(() => {});
  }, [getAccessTokenSilently]);

  useWorkflowWebSocket(id ?? null, token);

  const handleApprove = async (phase: WorkflowPhase) => {
    if (!id) return;
    await approve({ id, phase });
  };

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="h-8 bg-muted rounded w-48 animate-pulse" />
        <div className="h-64 bg-muted rounded animate-pulse" />
      </div>
    );
  }

  if (!workflow) {
    return (
      <div className="text-center py-20">
        <p className="text-muted-foreground">Workflow not found.</p>
        <Link to="/" className="text-blue-600 text-sm mt-2 inline-block">
          Back to dashboard
        </Link>
      </div>
    );
  }

  const allSteps = PHASE_ORDER.map((phase) => {
    const existing = workflow.steps.find((s) => s.phase === phase);
    return (
      existing ?? {
        id: `placeholder-${phase}`,
        phase,
        status: "PENDING" as const,
        duration: undefined,
        output: undefined,
        artifacts: undefined,
        started_at: undefined,
        completed_at: undefined,
      }
    );
  });

  return (
    <div className="space-y-6 max-w-3xl">
      <div>
        <Link
          to="/"
          className="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground mb-3"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Dashboard
        </Link>

        <div className="flex items-start justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="font-mono font-semibold text-flowguard-600 bg-flowguard-50 px-2 py-0.5 rounded text-sm">
                {workflow.task_id}
              </span>
              <Badge className={cn(WORKFLOW_STATUS_COLORS[workflow.status])}>
                {workflow.status}
              </Badge>
            </div>
            <h1 className="text-xl font-bold">{workflow.title}</h1>
            {workflow.description && (
              <p className="text-muted-foreground text-sm mt-1">{workflow.description}</p>
            )}
            <p className="text-xs text-muted-foreground mt-2">
              Started {formatDate(workflow.created_at)} · App: {workflow.target_app}
            </p>
          </div>

          <div className="flex gap-2 shrink-0">
            <Button variant="outline" size="sm" onClick={() => refetch()} className="gap-1.5">
              <RefreshCw className="w-3.5 h-3.5" />
              Refresh
            </Button>
            {workflow.github_pr_url && (
              <a href={workflow.github_pr_url} target="_blank" rel="noopener noreferrer">
                <Button variant="outline" size="sm" className="gap-1.5">
                  <GitBranch className="w-3.5 h-3.5" />
                  View PR
                </Button>
              </a>
            )}
            {workflow.jira_url && (
              <a href={workflow.jira_url} target="_blank" rel="noopener noreferrer">
                <Button variant="outline" size="sm" className="gap-1.5">
                  <ExternalLink className="w-3.5 h-3.5" />
                  Jira
                </Button>
              </a>
            )}
          </div>
        </div>
      </div>

      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base">7-Phase Delivery Workflow</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="pt-2">
            {allSteps.map((step, i) => (
              <PhaseStep
                key={step.phase}
                step={step}
                index={i}
                isLast={i === allSteps.length - 1}
                onApprove={handleApprove}
                canApprove={!isApproving}
              />
            ))}
          </div>
        </CardContent>
      </Card>

      {workflow.github_branch && (
        <Card>
          <CardContent className="p-4">
            <p className="text-sm">
              <span className="text-muted-foreground">Branch: </span>
              <code className="bg-muted px-1.5 py-0.5 rounded text-xs font-mono">
                {workflow.github_branch}
              </code>
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

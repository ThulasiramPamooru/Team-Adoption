import { useState } from "react";
import { Plus, TrendingUp, CheckCircle, XCircle, AlertTriangle, Activity } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { WorkflowCard } from "@/components/workflow/WorkflowCard";
import { RunWorkflowModal } from "@/components/workflow/RunWorkflowModal";
import { useWorkflows, useDashboardStats } from "@/hooks/useWorkflows";

function StatCard({
  title,
  value,
  icon: Icon,
  color,
}: {
  title: string;
  value: number | string;
  icon: React.ElementType;
  color: string;
}) {
  return (
    <Card>
      <CardContent className="p-5 flex items-center gap-4">
        <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${color}`}>
          <Icon className="w-5 h-5" />
        </div>
        <div>
          <p className="text-2xl font-bold">{value}</p>
          <p className="text-sm text-muted-foreground">{title}</p>
        </div>
      </CardContent>
    </Card>
  );
}

export function DashboardPage() {
  const [showModal, setShowModal] = useState(false);
  const { data: workflows, isLoading } = useWorkflows();
  const { data: stats } = useDashboardStats();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Dashboard</h1>
          <p className="text-muted-foreground text-sm">
            Safe engineering delivery for all your applications
          </p>
        </div>
        <Button onClick={() => setShowModal(true)} className="gap-2">
          <Plus className="w-4 h-4" />
          Run Workflow
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Runs"
          value={stats?.total_runs ?? 0}
          icon={Activity}
          color="bg-blue-100 text-blue-600"
        />
        <StatCard
          title="Completed"
          value={stats?.completed ?? 0}
          icon={CheckCircle}
          color="bg-green-100 text-green-600"
        />
        <StatCard
          title="Failed"
          value={stats?.failed ?? 0}
          icon={XCircle}
          color="bg-red-100 text-red-600"
        />
        <StatCard
          title="Success Rate"
          value={stats ? `${stats.success_rate}%` : "—"}
          icon={TrendingUp}
          color="bg-purple-100 text-purple-600"
        />
      </div>

      {/* Blocked alerts */}
      {stats && stats.blocked > 0 && (
        <div className="flex items-center gap-3 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <AlertTriangle className="w-5 h-5 text-yellow-600 shrink-0" />
          <p className="text-sm text-yellow-800">
            <span className="font-semibold">{stats.blocked} workflow{stats.blocked > 1 ? "s" : ""}</span> awaiting
            admin approval to continue.
          </p>
        </div>
      )}

      {/* Workflow list */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base">Recent Workflow Runs</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
              {Array.from({ length: 6 }).map((_, i) => (
                <div key={i} className="h-32 bg-muted rounded-lg animate-pulse" />
              ))}
            </div>
          ) : !workflows?.items.length ? (
            <div className="py-16 text-center">
              <p className="text-muted-foreground text-sm">No workflow runs yet.</p>
              <Button
                variant="outline"
                className="mt-4 gap-2"
                onClick={() => setShowModal(true)}
              >
                <Plus className="w-4 h-4" />
                Run your first workflow
              </Button>
            </div>
          ) : (
            <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
              {workflows.items.map((wf) => (
                <WorkflowCard key={wf.id} workflow={wf} />
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {showModal && <RunWorkflowModal onClose={() => setShowModal(false)} />}
    </div>
  );
}

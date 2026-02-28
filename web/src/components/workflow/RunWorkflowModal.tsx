import { useState } from "react";
import { X, Play } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useCreateWorkflow } from "@/hooks/useWorkflows";
import { useNavigate } from "react-router-dom";

interface RunWorkflowModalProps {
  onClose: () => void;
}

export function RunWorkflowModal({ onClose }: RunWorkflowModalProps) {
  const navigate = useNavigate();
  const { mutateAsync, isPending } = useCreateWorkflow();
  const [form, setForm] = useState({
    task_id: "DIPA-",
    target_app: "",
    title: "",
    description: "",
  });
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    if (!form.task_id.match(/^DIPA-\d+$/)) {
      setError("Task ID must be in format DIPA-123");
      return;
    }
    if (!form.target_app.trim()) {
      setError("Target application is required");
      return;
    }
    if (!form.title.trim()) {
      setError("Title is required");
      return;
    }
    try {
      const workflow = await mutateAsync(form);
      onClose();
      navigate(`/workflows/${workflow.id}`);
    } catch {
      setError("Failed to start workflow. Check your configuration.");
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="bg-background rounded-lg shadow-xl w-full max-w-md p-6">
        <div className="flex items-center justify-between mb-5">
          <h2 className="text-lg font-semibold">Run FlowGuard Workflow</h2>
          <button onClick={onClose} className="text-muted-foreground hover:text-foreground">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="text-sm font-medium block mb-1.5">JIRA Task ID</label>
            <Input
              value={form.task_id}
              onChange={(e) => setForm((f) => ({ ...f, task_id: e.target.value }))}
              placeholder="DIPA-123"
            />
          </div>

          <div>
            <label className="text-sm font-medium block mb-1.5">Target Application</label>
            <Input
              value={form.target_app}
              onChange={(e) => setForm((f) => ({ ...f, target_app: e.target.value }))}
              placeholder="e.g. my-app, backend-api"
            />
          </div>

          <div>
            <label className="text-sm font-medium block mb-1.5">Title</label>
            <Input
              value={form.title}
              onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))}
              placeholder="Fix: Navigation bug in step 3"
            />
          </div>

          <div>
            <label className="text-sm font-medium block mb-1.5">
              Description <span className="text-muted-foreground">(optional)</span>
            </label>
            <textarea
              value={form.description}
              onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
              placeholder="Describe the feature or bug fix..."
              rows={3}
              className="flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring resize-none"
            />
          </div>

          {error && (
            <p className="text-sm text-destructive">{error}</p>
          )}

          <div className="flex gap-3 pt-2">
            <Button type="button" variant="outline" onClick={onClose} className="flex-1">
              Cancel
            </Button>
            <Button type="submit" disabled={isPending} className="flex-1 gap-2">
              <Play className="w-4 h-4" />
              {isPending ? "Starting..." : "Run Workflow"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}

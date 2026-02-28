import { create } from "zustand";
import type { Workflow, WsMessage, WorkflowPhase, StepStatus } from "@/types";

interface WorkflowStore {
  workflows: Workflow[];
  activeWorkflow: Workflow | null;
  wsConnected: boolean;

  setWorkflows: (workflows: Workflow[]) => void;
  setActiveWorkflow: (workflow: Workflow | null) => void;
  updateWorkflowFromWs: (msg: WsMessage) => void;
  setWsConnected: (connected: boolean) => void;
}

export const useWorkflowStore = create<WorkflowStore>((set) => ({
  workflows: [],
  activeWorkflow: null,
  wsConnected: false,

  setWorkflows: (workflows) => set({ workflows }),

  setActiveWorkflow: (workflow) => set({ activeWorkflow: workflow }),

  setWsConnected: (wsConnected) => set({ wsConnected }),

  updateWorkflowFromWs: (msg) =>
    set((state) => {
      const updateSteps = (workflow: Workflow): Workflow => ({
        ...workflow,
        current_phase: (msg.phase as WorkflowPhase) ?? workflow.current_phase,
        status:
          msg.type === "workflow_complete"
            ? "COMPLETED"
            : msg.type === "workflow_failed"
            ? "FAILED"
            : "RUNNING",
        steps: workflow.steps.map((step) =>
          step.phase === msg.phase
            ? {
                ...step,
                status: (msg.status as StepStatus) ?? step.status,
                output: msg.output
                  ? (step.output ?? "") + "\n" + msg.output
                  : step.output,
              }
            : step
        ),
      });

      return {
        workflows: state.workflows.map((w) =>
          w.id === msg.workflow_id ? updateSteps(w) : w
        ),
        activeWorkflow:
          state.activeWorkflow?.id === msg.workflow_id
            ? updateSteps(state.activeWorkflow)
            : state.activeWorkflow,
      };
    }),
}));

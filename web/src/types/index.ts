// ─────────────────────────────────────────────
// FlowGuard — Core TypeScript Types
// ─────────────────────────────────────────────

export type UserRole = "admin" | "developer";

export interface User {
  id: string;
  email: string;
  name: string;
  role: UserRole;
  avatar?: string;
}

// ── Workflow State Machine ─────────────────────
export type WorkflowPhase =
  | "ANALYSIS"
  | "DOCUMENTED"
  | "SECURITY"
  | "TESTED"
  | "COMMITTED"
  | "PR_CREATED"
  | "DEPLOYED";

export const PHASE_ORDER: WorkflowPhase[] = [
  "ANALYSIS",
  "DOCUMENTED",
  "SECURITY",
  "TESTED",
  "COMMITTED",
  "PR_CREATED",
  "DEPLOYED",
];

export const PHASE_LABELS: Record<WorkflowPhase, string> = {
  ANALYSIS: "Impact Analysis",
  DOCUMENTED: "Documentation",
  SECURITY: "Security Review",
  TESTED: "E2E Testing",
  COMMITTED: "Git Commit",
  PR_CREATED: "Pull Request",
  DEPLOYED: "Deployment",
};

export const PHASE_DESCRIPTIONS: Record<WorkflowPhase, string> = {
  ANALYSIS: "Analyse impact on existing flows before making changes",
  DOCUMENTED: "Generate JIRA issue folder and .md documentation",
  SECURITY: "Scan for security vulnerabilities and browser compatibility",
  TESTED: "Run Playwright E2E tests and generate report",
  COMMITTED: "Create Git commit with test report summary",
  PR_CREATED: "Create branch (DIPA-ID) and GitHub Pull Request",
  DEPLOYED: "Pre-deploy gate check and final deployment",
};

export type StepStatus =
  | "PENDING"
  | "IN_PROGRESS"
  | "PASSED"
  | "BLOCKED"
  | "FAILED"
  | "SKIPPED";

export interface WorkflowStep {
  id: string;
  phase: WorkflowPhase;
  status: StepStatus;
  output?: string;
  duration?: number;
  started_at?: string;
  completed_at?: string;
  artifacts?: Record<string, string>;
}

export type WorkflowStatus =
  | "PENDING"
  | "RUNNING"
  | "COMPLETED"
  | "FAILED"
  | "BLOCKED"
  | "AWAITING_APPROVAL";

export interface Workflow {
  id: string;
  task_id: string;
  target_app: string;
  title: string;
  description?: string;
  status: WorkflowStatus;
  current_phase: WorkflowPhase | null;
  steps: WorkflowStep[];
  created_by: string;
  created_at: string;
  updated_at: string;
  jira_url?: string;
  github_pr_url?: string;
  github_branch?: string;
  test_report_path?: string;
}

export interface CreateWorkflowRequest {
  task_id: string;
  target_app: string;
  title: string;
  description?: string;
}

// ── Reports ───────────────────────────────────
export interface TestReport {
  id: string;
  workflow_id: string;
  task_id: string;
  passed: number;
  failed: number;
  skipped: number;
  total: number;
  duration_ms: number;
  html_path: string;
  json_path: string;
  summary: string;
  commit_message: string;
  created_at: string;
}

export interface SecurityReport {
  id: string;
  workflow_id: string;
  issues: SecurityIssue[];
  browser_compat: BrowserCompatIssue[];
  overall_status: "PASS" | "WARN" | "FAIL";
  created_at: string;
}

export interface SecurityIssue {
  severity: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  category: string;
  description: string;
  file?: string;
  line?: number;
  recommendation: string;
}

export interface BrowserCompatIssue {
  browser: string;
  issue: string;
  severity: "LOW" | "MEDIUM" | "HIGH";
  fix: string;
}

// ── Integrations ──────────────────────────────
export interface Integration {
  id: string;
  provider: "github" | "jira";
  connected: boolean;
  connected_at?: string;
  account?: string;
}

// ── WebSocket ─────────────────────────────────
export interface WsMessage {
  type:
    | "phase_update"
    | "step_output"
    | "workflow_complete"
    | "workflow_failed"
    | "approval_required";
  workflow_id: string;
  phase?: WorkflowPhase;
  status?: StepStatus;
  output?: string;
  timestamp: string;
}

// ── API Pagination ────────────────────────────
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
}

// ── Dashboard Stats ───────────────────────────
export interface DashboardStats {
  total_runs: number;
  completed: number;
  failed: number;
  blocked: number;
  running: number;
  success_rate: number;
}

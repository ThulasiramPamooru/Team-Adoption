import axios, { type AxiosInstance } from "axios";
import type {
  Workflow,
  CreateWorkflowRequest,
  PaginatedResponse,
  TestReport,
  SecurityReport,
  Integration,
  DashboardStats,
} from "@/types";

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
const DEV_MODE = import.meta.env.VITE_DEV_MODE === "true";

// In DEV_MODE, pre-set the token synchronously so first render has auth
let authToken: string | null = DEV_MODE ? "dev-local-token" : null;

export function setAuthToken(token: string | null) {
  authToken = token;
}

const api: AxiosInstance = axios.create({
  baseURL: `${BASE_URL}/api/v1`,
  timeout: 30000,
  headers: { "Content-Type": "application/json" },
});

// Attach JWT on every request
api.interceptors.request.use((config) => {
  if (authToken) {
    config.headers.Authorization = `Bearer ${authToken}`;
  }
  return config;
});

// Handle 401 globally
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      setAuthToken(null);
      window.location.href = "/login";
    }
    return Promise.reject(err);
  }
);

// ── Workflows ──────────────────────────────────
export const workflowsApi = {
  list: (page = 1, perPage = 20) =>
    api
      .get<PaginatedResponse<Workflow>>("/workflows", {
        params: { page, per_page: perPage },
      })
      .then((r) => r.data),

  get: (id: string) =>
    api.get<Workflow>(`/workflows/${id}`).then((r) => r.data),

  create: (data: CreateWorkflowRequest) =>
    api.post<Workflow>("/workflows", data).then((r) => r.data),

  approve: (id: string, phase: string) =>
    api.post<Workflow>(`/workflows/${id}/approve`, { phase }).then((r) => r.data),

  cancel: (id: string) =>
    api.post<Workflow>(`/workflows/${id}/cancel`).then((r) => r.data),

  retry: (id: string, phase: string) =>
    api.post<Workflow>(`/workflows/${id}/retry`, { phase }).then((r) => r.data),
};

// ── Reports ────────────────────────────────────
export const reportsApi = {
  getTestReport: (workflowId: string) =>
    api
      .get<TestReport>(`/reports/test/${workflowId}`)
      .then((r) => r.data),

  getSecurityReport: (workflowId: string) =>
    api
      .get<SecurityReport>(`/reports/security/${workflowId}`)
      .then((r) => r.data),

  listAll: (page = 1) =>
    api
      .get<PaginatedResponse<TestReport>>("/reports", {
        params: { page, per_page: 20 },
      })
      .then((r) => r.data),
};

// ── Dashboard ──────────────────────────────────
export const dashboardApi = {
  getStats: () =>
    api.get<DashboardStats>("/dashboard/stats").then((r) => r.data),
};

// ── Integrations ───────────────────────────────
export const integrationsApi = {
  list: () =>
    api.get<Integration[]>("/integrations").then((r) => r.data),

  saveGithub: (token: string) =>
    api.post("/integrations/github", { token }).then((r) => r.data),

  saveJira: (data: { url: string; email: string; token: string }) =>
    api.post("/integrations/jira", data).then((r) => r.data),

  test: (provider: string) =>
    api.post(`/integrations/${provider}/test`).then((r) => r.data),
};

// ── Auth ───────────────────────────────────────
export const authApi = {
  me: () => api.get("/auth/me").then((r) => r.data),
  syncUser: (auth0User: Record<string, unknown>) =>
    api.post("/auth/sync", auth0User).then((r) => r.data),
};

export default api;

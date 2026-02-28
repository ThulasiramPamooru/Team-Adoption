import { useEffect } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { useAuth0 } from "@auth0/auth0-react";
import { Loader2 } from "lucide-react";
import { AppLayout } from "@/components/layout/AppLayout";
import { LoginPage } from "@/pages/Login";
import { DashboardPage } from "@/pages/Dashboard";
import { WorkflowDetailPage } from "@/pages/WorkflowDetail";
import { ReportsPage } from "@/pages/Reports";
import { SettingsPage } from "@/pages/Settings";
import { setAuthToken, authApi } from "@/lib/api";

// DEV_MODE: skip Auth0 entirely when VITE_DEV_MODE=true
const DEV_MODE = import.meta.env.VITE_DEV_MODE === "true";

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading, getAccessTokenSilently } = useAuth0();

  // In DEV_MODE, use the magic dev token — no Auth0 required
  useEffect(() => {
    if (DEV_MODE) {
      setAuthToken("dev-local-token");
      authApi.me().catch(() => {});
      return;
    }
    if (isAuthenticated) {
      getAccessTokenSilently()
        .then((token) => {
          setAuthToken(token);
          authApi.me().catch(() => {});
        })
        .catch(() => {});
    }
  }, [isAuthenticated, getAccessTokenSilently]);

  // In DEV_MODE, always render children directly (no Auth0 redirect)
  if (DEV_MODE) return <>{children}</>;

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="w-6 h-6 animate-spin text-flowguard-500" />
      </div>
    );
  }

  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <AppLayout />
            </ProtectedRoute>
          }
        >
          <Route index element={<DashboardPage />} />
          <Route path="workflows" element={<DashboardPage />} />
          <Route path="workflows/:id" element={<WorkflowDetailPage />} />
          <Route path="reports" element={<ReportsPage />} />
          <Route path="settings" element={<SettingsPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

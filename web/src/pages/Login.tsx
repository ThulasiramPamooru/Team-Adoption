import { useAuth0 } from "@auth0/auth0-react";
import { Shield, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";

export function LoginPage() {
  const { loginWithRedirect, isLoading } = useAuth0();

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-flowguard-50 to-background">
      <div className="w-full max-w-sm p-8 bg-card rounded-2xl shadow-lg border">
        {/* Logo */}
        <div className="flex flex-col items-center mb-8">
          <div className="w-14 h-14 rounded-2xl bg-flowguard-500 flex items-center justify-center mb-4">
            <Shield className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-2xl font-bold tracking-tight">FlowGuard</h1>
          <p className="text-muted-foreground text-sm mt-1 text-center">
            AI Engineering Delivery Platform
          </p>
        </div>

        {/* Features */}
        <ul className="text-sm text-muted-foreground space-y-2 mb-8">
          {[
            "7-phase safe delivery workflow",
            "Playwright E2E test automation",
            "GitHub PR + Jira integration",
            "Security & browser compat review",
          ].map((f) => (
            <li key={f} className="flex items-center gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-flowguard-500" />
              {f}
            </li>
          ))}
        </ul>

        <Button
          onClick={() => loginWithRedirect()}
          disabled={isLoading}
          className="w-full bg-flowguard-500 hover:bg-flowguard-600"
          size="lg"
        >
          {isLoading ? (
            <Loader2 className="w-4 h-4 animate-spin mr-2" />
          ) : null}
          Sign in with Auth0
        </Button>

        <p className="text-xs text-muted-foreground text-center mt-4">
          Secure SSO — no password required
        </p>
      </div>
    </div>
  );
}

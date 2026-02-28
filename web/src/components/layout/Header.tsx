import { useAuth0 } from "@auth0/auth0-react";
import { Bell, LogOut, User } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useWorkflowStore } from "@/store/workflowStore";

export function Header() {
  const { user, logout } = useAuth0();
  const wsConnected = useWorkflowStore((s) => s.wsConnected);

  return (
    <header className="h-16 border-b bg-card flex items-center justify-between px-6">
      <div className="flex items-center gap-2">
        <span className="text-sm text-muted-foreground">
          Engineering Delivery Platform
        </span>
        <div className={`w-2 h-2 rounded-full ${wsConnected ? "bg-green-500" : "bg-muted"}`} title={wsConnected ? "Live" : "Offline"} />
      </div>

      <div className="flex items-center gap-3">
        <Button variant="ghost" size="icon">
          <Bell className="w-4 h-4" />
        </Button>

        <div className="flex items-center gap-2 border rounded-full px-3 py-1.5">
          <User className="w-4 h-4 text-muted-foreground" />
          <span className="text-sm font-medium">{user?.name ?? user?.email}</span>
        </div>

        <Button
          variant="ghost"
          size="icon"
          onClick={() => logout({ logoutParams: { returnTo: window.location.origin } })}
        >
          <LogOut className="w-4 h-4" />
        </Button>
      </div>
    </header>
  );
}

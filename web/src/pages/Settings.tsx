import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { Github, CheckCircle, XCircle, Loader2, Save } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { integrationsApi } from "@/lib/api";

export function SettingsPage() {
  const { data: integrations } = useQuery({
    queryKey: ["integrations"],
    queryFn: integrationsApi.list,
  });

  const [githubToken, setGithubToken] = useState("");
  const [jira, setJira] = useState({ url: "https://dolcera.atlassian.net", email: "", token: "" });
  const [savedMsg, setSavedMsg] = useState<string | null>(null);

  const saveGitHub = useMutation({
    mutationFn: () => integrationsApi.saveGithub(githubToken),
    onSuccess: () => { setSavedMsg("GitHub token saved."); setTimeout(() => setSavedMsg(null), 3000); },
  });

  const saveJira = useMutation({
    mutationFn: () => integrationsApi.saveJira(jira),
    onSuccess: () => { setSavedMsg("Jira credentials saved."); setTimeout(() => setSavedMsg(null), 3000); },
  });

  const githubIntegration = integrations?.find((i) => i.provider === "github");
  const jiraIntegration = integrations?.find((i) => i.provider === "jira");

  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h1 className="text-2xl font-bold">Settings</h1>
        <p className="text-muted-foreground text-sm">Configure integrations and preferences</p>
      </div>

      {savedMsg && (
        <div className="flex items-center gap-2 bg-green-50 border border-green-200 rounded-lg px-4 py-3 text-green-800 text-sm">
          <CheckCircle className="w-4 h-4" />
          {savedMsg}
        </div>
      )}

      {/* GitHub */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Github className="w-5 h-5" />
              <CardTitle className="text-base">GitHub Integration</CardTitle>
            </div>
            {githubIntegration?.connected ? (
              <span className="flex items-center gap-1 text-xs text-green-600">
                <CheckCircle className="w-3.5 h-3.5" /> Connected
              </span>
            ) : (
              <span className="flex items-center gap-1 text-xs text-muted-foreground">
                <XCircle className="w-3.5 h-3.5" /> Not connected
              </span>
            )}
          </div>
          <CardDescription>
            Repo: <code className="text-xs">ThulasiramPamooru/Team-Adoption</code>
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <div>
            <label className="text-sm font-medium block mb-1.5">Personal Access Token</label>
            <Input
              type="password"
              value={githubToken}
              onChange={(e) => setGithubToken(e.target.value)}
              placeholder="ghp_..."
            />
            <p className="text-xs text-muted-foreground mt-1">
              Needs: repo, pull_requests scopes
            </p>
          </div>
          <Button
            size="sm"
            onClick={() => saveGitHub.mutate()}
            disabled={!githubToken || saveGitHub.isPending}
            className="gap-2"
          >
            {saveGitHub.isPending ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Save className="w-3.5 h-3.5" />}
            Save Token
          </Button>
        </CardContent>
      </Card>

      {/* Jira */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-base">Jira Integration</CardTitle>
            {jiraIntegration?.connected ? (
              <span className="flex items-center gap-1 text-xs text-green-600">
                <CheckCircle className="w-3.5 h-3.5" /> Connected
              </span>
            ) : (
              <span className="flex items-center gap-1 text-xs text-muted-foreground">
                <XCircle className="w-3.5 h-3.5" /> Not connected
              </span>
            )}
          </div>
          <CardDescription>
            Project: <code className="text-xs">DIPA</code> · dolcera.atlassian.net
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="grid gap-3">
            <div>
              <label className="text-sm font-medium block mb-1.5">Jira Email</label>
              <Input
                type="email"
                value={jira.email}
                onChange={(e) => setJira((j) => ({ ...j, email: e.target.value }))}
                placeholder="you@dolcera.com"
              />
            </div>
            <div>
              <label className="text-sm font-medium block mb-1.5">API Token</label>
              <Input
                type="password"
                value={jira.token}
                onChange={(e) => setJira((j) => ({ ...j, token: e.target.value }))}
                placeholder="Jira API token"
              />
              <p className="text-xs text-muted-foreground mt-1">
                Generate at: id.atlassian.com/manage-profile/security/api-tokens
              </p>
            </div>
          </div>
          <Button
            size="sm"
            onClick={() => saveJira.mutate()}
            disabled={!jira.email || !jira.token || saveJira.isPending}
            className="gap-2"
          >
            {saveJira.isPending ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Save className="w-3.5 h-3.5" />}
            Save Credentials
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}

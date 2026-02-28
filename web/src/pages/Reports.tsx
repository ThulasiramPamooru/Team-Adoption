import { useQuery } from "@tanstack/react-query";
import { FileText, CheckCircle, XCircle, Clock } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { reportsApi } from "@/lib/api";
import { formatDate, formatDuration } from "@/lib/utils";

export function ReportsPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["reports"],
    queryFn: () => reportsApi.listAll(),
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Test Reports</h1>
        <p className="text-muted-foreground text-sm">
          Playwright E2E test results stored in <code className="bg-muted px-1 rounded text-xs">test-reports/</code>
        </p>
      </div>

      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base">All Reports</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-3">
              {Array.from({ length: 4 }).map((_, i) => (
                <div key={i} className="h-16 bg-muted rounded animate-pulse" />
              ))}
            </div>
          ) : !data?.items.length ? (
            <div className="py-16 text-center">
              <FileText className="w-10 h-10 text-muted-foreground mx-auto mb-3" />
              <p className="text-muted-foreground text-sm">No test reports yet.</p>
              <p className="text-xs text-muted-foreground mt-1">
                Reports appear here after the TESTED phase completes.
              </p>
            </div>
          ) : (
            <div className="divide-y">
              {data.items.map((report) => (
                <div key={report.id} className="py-4 flex items-center justify-between gap-4">
                  <div>
                    <div className="flex items-center gap-2 mb-0.5">
                      <span className="font-mono text-xs font-semibold text-flowguard-600 bg-flowguard-50 px-1.5 py-0.5 rounded">
                        {report.task_id}
                      </span>
                      <span className="text-sm font-medium">{report.summary}</span>
                    </div>
                    <div className="flex items-center gap-3 text-xs text-muted-foreground">
                      <span className="flex items-center gap-1 text-green-600">
                        <CheckCircle className="w-3 h-3" />
                        {report.passed} passed
                      </span>
                      {report.failed > 0 && (
                        <span className="flex items-center gap-1 text-red-600">
                          <XCircle className="w-3 h-3" />
                          {report.failed} failed
                        </span>
                      )}
                      <span className="flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {formatDuration(report.duration_ms)}
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 shrink-0">
                    <Badge variant={report.failed === 0 ? "success" : "destructive"}>
                      {report.failed === 0 ? "PASS" : "FAIL"}
                    </Badge>
                    <div className="text-xs text-muted-foreground">
                      {formatDate(report.created_at)}
                    </div>
                    {report.html_path && (
                      <a
                        href={`/api/v1/reports/file/${report.id}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xs text-blue-600 underline"
                      >
                        View HTML
                      </a>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

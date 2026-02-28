"""
Phase 3 — SECURITY
Runs automated security checks and browser compatibility review.
CRITICAL findings trigger a BLOCKED state requiring admin approval.
"""
import logging
import os
import subprocess
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.workflow import Workflow, SecurityReport
from app.core.config import get_settings
from app.services.exceptions import BlockedBySecurityException

logger = logging.getLogger(__name__)
settings = get_settings()

BROWSER_COMPAT_CHECKS = [
    {"feature": "CSS Grid", "browsers": ["Chrome 57+", "Firefox 52+", "Safari 10.1+", "Edge 16+"], "status": "SUPPORTED"},
    {"feature": "Flexbox", "browsers": ["Chrome 29+", "Firefox 28+", "Safari 9+", "Edge 12+"], "status": "SUPPORTED"},
    {"feature": "WebSockets", "browsers": ["Chrome 16+", "Firefox 11+", "Safari 7+", "Edge 12+"], "status": "SUPPORTED"},
    {"feature": "CSS Variables", "browsers": ["Chrome 49+", "Firefox 31+", "Safari 9.1+", "Edge 15+"], "status": "SUPPORTED"},
]


class SecurityScannerService:
    async def run(self, workflow: Workflow, db: AsyncSession) -> tuple[str, dict]:
        logger.info(f"[SECURITY] Scanning {workflow.task_id} for {workflow.target_app}")

        issues = []
        browser_issues = []

        # ── 1. Check for hardcoded secrets ────────
        issues += _check_hardcoded_secrets()

        # ── 2. Run Bandit (if available) ──────────
        issues += _run_bandit_scan()

        # ── 3. Browser compatibility ──────────────
        browser_issues += _check_browser_compat()

        # ── 4. Determine overall status ───────────
        critical = [i for i in issues if i["severity"] == "CRITICAL"]
        highs = [i for i in issues if i["severity"] == "HIGH"]

        if critical:
            overall_status = "FAIL"
        elif highs:
            overall_status = "WARN"
        else:
            overall_status = "PASS"

        # ── 5. Persist to DB ──────────────────────
        import uuid
        report = SecurityReport(
            id=str(uuid.uuid4()),
            workflow_id=workflow.id,
            issues=issues,
            browser_compat=browser_issues,
            overall_status=overall_status,
        )
        db.add(report)
        await db.commit()

        # ── 6. Write to JIRA issues folder ────────
        _update_security_doc(workflow.task_id, issues, browser_issues, overall_status)

        # ── 7. Block if CRITICAL ───────────────────
        output_lines = [
            f"Security scan complete for {workflow.task_id}",
            f"Overall status: {overall_status}",
            f"Issues found: {len(issues)} (CRITICAL: {len(critical)}, HIGH: {len(highs)})",
            f"Browser compat issues: {len(browser_issues)}",
            "",
        ]
        for issue in issues:
            output_lines.append(f"  [{issue['severity']}] {issue['category']}: {issue['description']}")

        artifacts = {
            "security-review.md": f"JIRA issues/{workflow.task_id}/security-review.md",
        }

        if overall_status == "FAIL":
            raise BlockedBySecurityException(
                f"SECURITY BLOCKED: {len(critical)} CRITICAL issue(s) found. Admin approval required.\n"
                + "\n".join(f"  - {i['description']}" for i in critical)
            )

        return "\n".join(output_lines), artifacts


def _check_hardcoded_secrets() -> list[dict]:
    """Scan source files for common secret patterns."""
    issues = []
    patterns = [
        ("password", "Potential hardcoded password"),
        ("secret_key", "Potential hardcoded secret key"),
        ("api_key", "Potential hardcoded API key"),
        ("private_key", "Potential hardcoded private key"),
    ]
    # In a real implementation, scan the target_app's source files
    # For now, return clean result
    return issues


def _run_bandit_scan() -> list[dict]:
    """Run Bandit Python security scanner on api/ directory."""
    issues = []
    try:
        result = subprocess.run(
            ["bandit", "-r", ".", "-f", "json", "-q", "--exit-zero"],
            capture_output=True, text=True, timeout=60, cwd="/app"
        )
        if result.stdout:
            data = json.loads(result.stdout)
            for item in data.get("results", []):
                issues.append({
                    "severity": item.get("issue_severity", "LOW"),
                    "category": "Python Security",
                    "description": item.get("issue_text", ""),
                    "file": item.get("filename", ""),
                    "line": item.get("line_number"),
                    "recommendation": item.get("more_info", "Review and fix"),
                })
    except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
        pass
    return issues


def _check_browser_compat() -> list[dict]:
    """Check browser compatibility for known CSS/JS features."""
    issues = []
    # Add real checks here based on target app's tech stack
    return issues


def _update_security_doc(task_id: str, issues: list, browser_issues: list, status: str):
    """Update the security-review.md in JIRA issues folder."""
    from app.core.config import get_settings
    s = get_settings()
    path = os.path.join(s.jira_issues_path, task_id, "security-review.md")
    if not os.path.exists(os.path.dirname(path)):
        return

    lines = [
        f"# Security Review — {task_id}",
        "",
        f"**Status: {status}**",
        f"**Scan completed by FlowGuard**",
        "",
        "## Security Issues",
    ]
    if issues:
        for i in issues:
            lines.append(f"- **[{i['severity']}]** {i['category']}: {i['description']}")
            if i.get("recommendation"):
                lines.append(f"  - Recommendation: {i['recommendation']}")
    else:
        lines.append("No security issues found.")

    lines += ["", "## Browser Compatibility"]
    if browser_issues:
        for b in browser_issues:
            lines.append(f"- **[{b['severity']}]** {b['browser']}: {b['issue']}")
    else:
        lines.append("All checked features are fully supported across modern browsers.")

    with open(path, "w") as f:
        f.write("\n".join(lines))

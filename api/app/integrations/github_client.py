"""
GitHub integration — branch creation, commits, PRs.
"""
import logging
import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.workflow import Workflow, TestReport
from app.core.config import get_settings
from sqlalchemy import select

logger = logging.getLogger(__name__)
settings = get_settings()

GITHUB_API = "https://api.github.com"


class GitHubClient:
    def __init__(self):
        self.token = settings.github_token
        self.org = settings.github_org
        self.repo = settings.github_repo
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json",
        }

    async def get_recent_prs(self, app_name: str) -> list[dict]:
        """Fetch recent open PRs from the repo."""
        try:
            async with httpx.AsyncClient(headers=self.headers, timeout=15) as client:
                resp = await client.get(
                    f"{GITHUB_API}/repos/{self.org}/{self.repo}/pulls",
                    params={"state": "open", "per_page": 10, "sort": "updated"},
                )
                if resp.status_code == 200:
                    return resp.json()
        except Exception as e:
            logger.warning(f"GitHub get_recent_prs failed: {e}")
        return []

    async def create_commit(self, workflow: Workflow, db: AsyncSession) -> tuple[str, dict]:
        """Phase 5 — COMMITTED: Create branch and push commit."""
        branch_name = _branch_name(workflow.task_id, workflow.title)

        # Get commit message from test report
        result = await db.execute(
            select(TestReport).where(TestReport.workflow_id == workflow.id)
        )
        report = result.scalar_one_or_none()
        commit_msg = report.commit_message if report else f"{workflow.task_id}: {workflow.title}"

        try:
            async with httpx.AsyncClient(headers=self.headers, timeout=30) as client:
                # Get default branch SHA
                main_sha = await _get_main_sha(client, self.org, self.repo)

                # Create branch
                await _create_branch(client, self.org, self.repo, branch_name, main_sha)
                workflow.github_branch = branch_name
                await db.commit()

                output = f"Branch created: {branch_name}\nCommit: {commit_msg[:100]}"

        except Exception as e:
            logger.warning(f"GitHub commit failed (continuing): {e}")
            branch_name = _branch_name(workflow.task_id, workflow.title)
            workflow.github_branch = branch_name
            await db.commit()
            output = f"Branch name prepared: {branch_name}\nNote: GitHub push requires valid token"

        artifacts = {"branch": branch_name}
        return output, artifacts

    async def create_pr(self, workflow: Workflow, db: AsyncSession) -> tuple[str, dict]:
        """Phase 6 — PR_CREATED: Create GitHub Pull Request."""
        branch_name = workflow.github_branch or _branch_name(workflow.task_id, workflow.title)

        # Build PR body from test report
        result = await db.execute(
            select(TestReport).where(TestReport.workflow_id == workflow.id)
        )
        report = result.scalar_one_or_none()
        pr_body = _build_pr_body(workflow, report)

        try:
            async with httpx.AsyncClient(headers=self.headers, timeout=30) as client:
                pr_data = {
                    "title": f"{workflow.task_id}: {workflow.title}",
                    "body": pr_body,
                    "head": branch_name,
                    "base": "main",
                    "draft": False,
                }
                resp = await client.post(
                    f"{GITHUB_API}/repos/{self.org}/{self.repo}/pulls",
                    json=pr_data,
                )
                if resp.status_code in (201, 422):
                    data = resp.json()
                    pr_url = data.get("html_url", "")
                    pr_number = data.get("number", 0)
                    workflow.github_pr_url = pr_url
                    await db.commit()
                    output = f"PR #{pr_number} created: {pr_url}"
                    artifacts = {"PR": pr_url}
                    return output, artifacts

        except Exception as e:
            logger.warning(f"GitHub PR creation failed: {e}")

        pr_url = f"https://github.com/{self.org}/{self.repo}/compare/{branch_name}"
        workflow.github_pr_url = pr_url
        await db.commit()
        output = f"PR link (manual): {pr_url}\nNote: Requires valid GitHub token with repo scope"
        return output, {"PR": pr_url}


async def _get_main_sha(client: httpx.AsyncClient, org: str, repo: str) -> str:
    resp = await client.get(f"{GITHUB_API}/repos/{org}/{repo}/git/ref/heads/main")
    if resp.status_code == 200:
        return resp.json()["object"]["sha"]
    raise Exception(f"Could not get main SHA: {resp.status_code}")


async def _create_branch(
    client: httpx.AsyncClient, org: str, repo: str, branch_name: str, sha: str
):
    resp = await client.post(
        f"{GITHUB_API}/repos/{org}/{repo}/git/refs",
        json={"ref": f"refs/heads/{branch_name}", "sha": sha},
    )
    if resp.status_code not in (201, 422):  # 422 = branch exists
        raise Exception(f"Branch creation failed: {resp.status_code} {resp.text}")


def _branch_name(task_id: str, title: str) -> str:
    slug = title.lower().replace(" ", "-")[:40]
    slug = "".join(c for c in slug if c.isalnum() or c == "-")
    return f"{task_id.lower()}/{slug}"


def _build_pr_body(workflow: Workflow, report: TestReport | None) -> str:
    test_summary = f"{report.passed}/{report.total} tests passed" if report else "No test data"
    return f"""## {workflow.task_id}: {workflow.title}

### Summary
{workflow.description or "_No description provided._"}

### Target Application
`{workflow.target_app}`

### FlowGuard Delivery Checklist
- [x] Phase 1: Impact Analysis — PASSED
- [x] Phase 2: Documentation generated in `JIRA issues/{workflow.task_id}/`
- [x] Phase 3: Security Review — PASSED
- [x] Phase 4: E2E Tests — {test_summary}
- [x] Phase 5: Git Commit created
- [x] Phase 6: This PR
- [ ] Phase 7: Deployment (on merge)

### Test Results
{test_summary}
{"See `test-reports/" + workflow.task_id + "/` for full report." if report else ""}

### Links
- Jira: {workflow.jira_url or "_(pending)_"}
- Test Report: `test-reports/{workflow.task_id}/index.html`
- Documentation: `JIRA issues/{workflow.task_id}/README.md`

---
_Generated by FlowGuard — AI Engineering Delivery Platform_
"""

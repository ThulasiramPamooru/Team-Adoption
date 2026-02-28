"""
Jira Cloud integration — issue status updates, comments.
"""
import logging
import httpx
import base64
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

JIRA_API = f"{settings.jira_url}/rest/api/3"


class JiraClient:
    def __init__(self):
        self.url = settings.jira_url
        self.email = settings.jira_email
        self.token = settings.jira_api_token
        token = base64.b64encode(f"{self.email}:{self.token}".encode()).decode()
        self.headers = {
            "Authorization": f"Basic {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    async def get_issue(self, task_id: str) -> dict | None:
        try:
            async with httpx.AsyncClient(headers=self.headers, timeout=15) as client:
                resp = await client.get(f"{self.url}/rest/api/3/issue/{task_id}")
                if resp.status_code == 200:
                    return resp.json()
        except Exception as e:
            logger.warning(f"Jira get_issue failed: {e}")
        return None

    async def update_issue_status(self, task_id: str, status: str) -> str | None:
        """Move Jira issue to a transition (e.g. 'In Progress')."""
        issue_url = f"{self.url}/browse/{task_id}"
        try:
            async with httpx.AsyncClient(headers=self.headers, timeout=15) as client:
                # Get available transitions
                resp = await client.get(
                    f"{self.url}/rest/api/3/issue/{task_id}/transitions"
                )
                if resp.status_code != 200:
                    return issue_url

                transitions = resp.json().get("transitions", [])
                target = next(
                    (t for t in transitions if status.lower() in t["name"].lower()),
                    None,
                )
                if target:
                    await client.post(
                        f"{self.url}/rest/api/3/issue/{task_id}/transitions",
                        json={"transition": {"id": target["id"]}},
                    )
        except Exception as e:
            logger.warning(f"Jira status update failed: {e}")

        return issue_url

    async def add_comment(self, task_id: str, comment: str) -> bool:
        """Post a comment on a Jira issue."""
        try:
            async with httpx.AsyncClient(headers=self.headers, timeout=15) as client:
                resp = await client.post(
                    f"{self.url}/rest/api/3/issue/{task_id}/comment",
                    json={
                        "body": {
                            "type": "doc",
                            "version": 1,
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [{"type": "text", "text": comment}],
                                }
                            ],
                        }
                    },
                )
                return resp.status_code == 201
        except Exception as e:
            logger.warning(f"Jira add_comment failed: {e}")
            return False

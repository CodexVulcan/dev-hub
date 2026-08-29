"""
github_service.py — GitHub REST API client for pipeline status enrichment.

Security contract:
  - The GitHub token is read ONLY from os.environ.get("GITHUB_TOKEN").
  - The token is never hardcoded, never logged, never returned in API responses.
  - .env is excluded by .bobignore and .gitignore — Bob never reads it.
  - If GITHUB_TOKEN is absent the service returns "pending" without raising.
"""
import os
from typing import Optional
import httpx

GITHUB_API = "https://api.github.com"

# Map GitHub workflow conclusion/status values to DevHub stage statuses
_CONCLUSION_MAP = {
    "success":   "passing",
    "completed": "passing",
    "failure":   "failing",
    "timed_out": "failing",
    "cancelled": "failing",
    "in_progress": "running",
    "queued":    "pending",
    "waiting":   "pending",
    None:        "pending",
}


async def fetch_workflow_status(owner: str, repo: str, token: Optional[str] = None) -> dict:
    """
    Fetch the latest GitHub Actions workflow run for owner/repo.

    Returns:
        { "status": "passing"|"failing"|"running"|"pending", "reason": str|None }

    Never raises — all errors return { "status": "pending", "reason": "<message>" }.
    """
    resolved_token = token or os.environ.get("GITHUB_TOKEN")

    if not resolved_token:
        return {"status": "pending", "reason": "no_token"}

    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Authorization": f"Bearer {resolved_token}",
    }

    url = f"{GITHUB_API}/repos/{owner}/{repo}/actions/runs?per_page=1"

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.get(url, headers=headers)

        if resp.status_code == 404:
            return {"status": "pending", "reason": "repo_not_found"}
        if resp.status_code == 401:
            return {"status": "pending", "reason": "invalid_token"}
        if not resp.is_success:
            return {"status": "pending", "reason": f"github_http_{resp.status_code}"}

        data = resp.json()
        runs = data.get("workflow_runs", [])
        if not runs:
            return {"status": "pending", "reason": "no_runs"}

        latest = runs[0]
        conclusion = latest.get("conclusion") or latest.get("status")
        mapped = _CONCLUSION_MAP.get(conclusion, "pending")
        return {"status": mapped, "reason": None}

    except httpx.TimeoutException:
        return {"status": "pending", "reason": "timeout"}
    except Exception as exc:
        return {"status": "pending", "reason": f"error: {type(exc).__name__}"}

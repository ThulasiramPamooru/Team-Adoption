# FlowGuard — AI Engineering Delivery Platform

> Safe, tested, reviewed feature delivery in 7 locked phases.
> Built for **Team Adoption** at IP Author — integrates with **Jira DIPA**, **GitHub**, and **Playwright**.

---

## What is FlowGuard?

FlowGuard is an AI Engineering Orchestration Agent that ensures every feature or bug fix goes through a mandatory 7-phase delivery pipeline before reaching production — preventing regressions, security gaps, and untested deployments.

### Target App: `drafting-ai`

---

## The 7-Phase Workflow

| Phase | Name | What Happens |
|-------|------|-------------|
| 1 | **ANALYSIS** | Impact analysis on existing flows |
| 2 | **DOCUMENTED** | JIRA issue folder + `.md` docs auto-generated |
| 3 | **SECURITY** | Bandit scan + browser compat check |
| 4 | **TESTED** | Playwright E2E tests + HTML report |
| 5 | **COMMITTED** | Git commit from test report |
| 6 | **PR_CREATED** | Branch `DIPA-123/title` + GitHub PR |
| 7 | **DEPLOYED** | Pre-deploy gate → Vercel + Render |

Each phase: `PENDING → IN_PROGRESS → PASSED` (or `BLOCKED` requiring admin approval)

---

## Quick Start

### Prerequisites
- Node.js 20+
- Python 3.11+
- Docker + Docker Compose (for local full-stack)

### 1. Clone & Configure
```bash
git clone https://github.com/ThulasiramPamooru/Team-Adoption.git
cd Team-Adoption
cp .env.example .env
# Fill in your Auth0, GitHub, Jira credentials
```

### 2. Run with Docker
```bash
docker-compose up
```
- Web: http://localhost:5173
- API: http://localhost:8000/api/docs

### 3. Run without Docker

**Backend:**
```bash
cd api && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

**Frontend:**
```bash
cd web && npm install && npm run dev
```

### 4. Install CLI
```bash
cd cli && pip install -e .
flowguard run DIPA-123 --app drafting-ai --title "Fix: nav bug"
```

---

## CLI Commands

```bash
flowguard run DIPA-123 --app drafting-ai --title "Feature: X"
flowguard status DIPA-123
flowguard report DIPA-123
flowguard list
```

---

## Project Structure

```
Team-Adoption/
├── web/                    # React 18 + Tailwind + shadcn/ui
├── api/                    # FastAPI + PostgreSQL + SQLAlchemy
├── cli/                    # Python CLI (flowguard)
├── JIRA issues/            # Auto-created per task (DIPA-123/)
├── test-reports/           # Playwright HTML reports per task
├── .github/workflows/      # CI + Deploy (GitHub Actions)
├── docker-compose.yml
└── .env.example
```

---

## Roles

| Role | Permissions |
|------|-------------|
| **Admin** | Full access, approve BLOCKED phases, manage users |
| **Developer** | Create runs, view workflows, run tests, create PRs |

---

## Free Hosting

| Service | Platform |
|---------|----------|
| Frontend | Vercel (auto-deploy on push to `main`) |
| Backend | Render.com |
| Database | Render PostgreSQL |
| CI/CD | GitHub Actions |

---

## Required GitHub Secrets

Add at: `https://github.com/ThulasiramPamooru/Team-Adoption/settings/secrets/actions`

| Secret | Description |
|--------|-------------|
| `AUTH0_DOMAIN` | Auth0 domain |
| `AUTH0_CLIENT_ID` | Auth0 client ID |
| `API_URL` | Render backend URL |
| `WS_URL` | Render WebSocket URL (`wss://...`) |
| `VERCEL_TOKEN` | Vercel deploy token |
| `VERCEL_ORG_ID` | Vercel org ID |
| `VERCEL_PROJECT_ID` | Vercel project ID |
| `RENDER_DEPLOY_HOOK` | Render deploy hook URL |

---

*FlowGuard v1.0.0 — Built by IP Author Engineering*

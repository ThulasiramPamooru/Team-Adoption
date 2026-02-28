"""
FlowGuard Workflow Engine — 7-Phase State Machine
Phases run sequentially. Each phase updates DB + broadcasts via WebSocket.
"""
import asyncio
import logging
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models.workflow import Workflow, WorkflowStep
from app.services.websocket_manager import manager
from app.services.exceptions import BlockedBySecurityException

logger = logging.getLogger(__name__)

PHASES = [
    "ANALYSIS",
    "DOCUMENTED",
    "SECURITY",
    "TESTED",
    "COMMITTED",
    "PR_CREATED",
    "DEPLOYED",
]


class WorkflowEngine:
    async def run(self, workflow_id: str):
        """Execute all 7 phases from the beginning."""
        await self._execute_phases(workflow_id, start_from=None)

    async def resume(self, workflow_id: str, from_phase: str | None = None):
        """Resume execution from a specific phase (after admin approval)."""
        await self._execute_phases(workflow_id, start_from=from_phase)

    async def _execute_phases(self, workflow_id: str, start_from: str | None):
        async with AsyncSessionLocal() as db:
            try:
                result = await db.execute(select(Workflow).where(Workflow.id == workflow_id))
                workflow = result.scalar_one_or_none()
                if not workflow:
                    logger.error(f"Workflow {workflow_id} not found")
                    return

                workflow.status = "RUNNING"
                await db.commit()
                await db.refresh(workflow)

                start_idx = 0
                if start_from and start_from in PHASES:
                    start_idx = PHASES.index(start_from)

                for phase in PHASES[start_idx:]:
                    await self._run_phase(workflow_id, phase, db)

                    # Re-fetch workflow to check if it was blocked/failed
                    await db.refresh(workflow)
                    if workflow.status in ("BLOCKED", "FAILED", "AWAITING_APPROVAL"):
                        break

                # If all phases PASSED → mark COMPLETED
                await db.refresh(workflow)
                if workflow.status == "RUNNING":
                    workflow.status = "COMPLETED"
                    await db.commit()
                    await manager.broadcast(workflow_id, {
                        "type": "workflow_complete",
                        "workflow_id": workflow_id,
                        "timestamp": datetime.utcnow().isoformat(),
                    })

            except Exception as exc:
                logger.exception(f"Workflow {workflow_id} crashed: {exc}")
                await self._mark_failed(workflow_id, str(exc), db)

    async def _run_phase(self, workflow_id: str, phase: str, db: AsyncSession):
        """Run a single phase, update step status, broadcast progress."""
        # Get the step
        result = await db.execute(
            select(WorkflowStep).where(
                WorkflowStep.workflow_id == workflow_id,
                WorkflowStep.phase == phase,
            )
        )
        step = result.scalar_one_or_none()
        if not step:
            logger.warning(f"No step found for {phase} in workflow {workflow_id}")
            return

        # Mark IN_PROGRESS
        step.status = "IN_PROGRESS"
        step.started_at = datetime.utcnow()
        await db.commit()
        await manager.broadcast(workflow_id, {
            "type": "phase_update",
            "workflow_id": workflow_id,
            "phase": phase,
            "status": "IN_PROGRESS",
            "timestamp": datetime.utcnow().isoformat(),
        })

        # Update workflow.current_phase
        wf_result = await db.execute(select(Workflow).where(Workflow.id == workflow_id))
        workflow = wf_result.scalar_one()
        workflow.current_phase = phase
        await db.commit()

        start_time = datetime.utcnow()
        try:
            output, artifacts = await self._execute_phase(phase, workflow_id, db)

            elapsed = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            step.status = "PASSED"
            step.output = output
            step.duration_ms = elapsed
            step.artifacts = artifacts
            step.completed_at = datetime.utcnow()
            await db.commit()

            await manager.broadcast(workflow_id, {
                "type": "phase_update",
                "workflow_id": workflow_id,
                "phase": phase,
                "status": "PASSED",
                "output": output,
                "timestamp": datetime.utcnow().isoformat(),
            })

        except BlockedBySecurityException as exc:
            step.status = "BLOCKED"
            step.output = str(exc)
            step.completed_at = datetime.utcnow()
            workflow.status = "AWAITING_APPROVAL"
            await db.commit()
            await manager.broadcast(workflow_id, {
                "type": "approval_required",
                "workflow_id": workflow_id,
                "phase": phase,
                "status": "BLOCKED",
                "output": str(exc),
                "timestamp": datetime.utcnow().isoformat(),
            })

        except Exception as exc:
            elapsed = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            step.status = "FAILED"
            step.output = f"ERROR: {str(exc)}"
            step.duration_ms = elapsed
            step.completed_at = datetime.utcnow()
            workflow.status = "FAILED"
            await db.commit()
            await manager.broadcast(workflow_id, {
                "type": "workflow_failed",
                "workflow_id": workflow_id,
                "phase": phase,
                "status": "FAILED",
                "output": str(exc),
                "timestamp": datetime.utcnow().isoformat(),
            })

    async def _execute_phase(
        self, phase: str, workflow_id: str, db: AsyncSession
    ) -> tuple[str, dict]:
        """Dispatch to the correct service for each phase.
        Lazy imports prevent circular dependencies.
        """
        wf_result = await db.execute(select(Workflow).where(Workflow.id == workflow_id))
        workflow = wf_result.scalar_one()

        if phase == "ANALYSIS":
            from app.services.analysis_service import AnalysisService
            return await AnalysisService().run(workflow, db)

        elif phase == "DOCUMENTED":
            from app.services.docs_generator import DocsGeneratorService
            return await DocsGeneratorService().run(workflow, db)

        elif phase == "SECURITY":
            from app.services.security_scanner import SecurityScannerService
            return await SecurityScannerService().run(workflow, db)

        elif phase == "TESTED":
            from app.services.test_runner import TestRunnerService
            return await TestRunnerService().run(workflow, db)

        elif phase == "COMMITTED":
            from app.integrations.github_client import GitHubClient
            return await GitHubClient().create_commit(workflow, db)

        elif phase == "PR_CREATED":
            from app.integrations.github_client import GitHubClient
            return await GitHubClient().create_pr(workflow, db)

        elif phase == "DEPLOYED":
            from app.services.deploy_service import DeployService
            return await DeployService().run(workflow, db)

        else:
            raise ValueError(f"Unknown phase: {phase}")

    async def _mark_failed(self, workflow_id: str, reason: str, db: AsyncSession):
        result = await db.execute(select(Workflow).where(Workflow.id == workflow_id))
        workflow = result.scalar_one_or_none()
        if workflow:
            workflow.status = "FAILED"
            await db.commit()


# BlockedBySecurityException lives in app.services.exceptions to avoid circular imports

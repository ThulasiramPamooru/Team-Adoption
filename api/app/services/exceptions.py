"""Shared exceptions for FlowGuard services — avoids circular imports."""


class BlockedBySecurityException(Exception):
    """Raised when the security phase finds CRITICAL issues requiring admin approval."""
    pass


class WorkflowPhaseException(Exception):
    """Generic phase execution failure."""
    pass

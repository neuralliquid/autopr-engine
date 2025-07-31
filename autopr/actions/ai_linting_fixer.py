"""
AI-Powered Linting Fixer.

Integrates with AutoPR's LLM infrastructure to automatically fix linting issues
using AI agents specialized for different types of code quality problems.
"""

import logging
import os
from collections.abc import Callable
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# =============================================================================
# ORCHESTRATION CONFIGURATION
# =============================================================================


class OrchestrationConfig(BaseModel):
    """Configuration for workflow orchestration systems."""

    enabled: bool = False
    orchestrator_type: str = "none"  # none, temporal, celery, prefect, airflow

    # Temporal.io configuration
    temporal: dict[str, Any] = Field(
        default_factory=lambda: {
            "namespace": "default",
            "task_queue": "ai-linting-queue",
            "address": "localhost:7233",
            "tls_enabled": False,
            "api_key_env": "TEMPORAL_API_KEY",
        }
    )

    # Celery configuration
    celery: dict[str, Any] = Field(
        default_factory=lambda: {
            "broker_url": "redis://localhost:6379/0",
            "result_backend": "redis://localhost:6379/0",
            "task_name": "ai_linting_task",
        }
    )

    # Prefect configuration
    prefect: dict[str, Any] = Field(
        default_factory=lambda: {"flow_name": "ai_linting_flow", "task_name": "ai_linting_task"}
    )

    # Fallback configuration
    fallback_to_standalone: bool = True


def detect_available_orchestrators() -> dict[str, bool]:
    """Detect which orchestration systems are available."""
    availability = {"temporal": False, "celery": False, "prefect": False, "airflow": False}

    # Check Temporal.io
    try:
        import temporalio  # noqa: F401

        # Check if environment variables are set
        if os.getenv("TEMPORAL_API_KEY") or os.getenv("TEMPORAL_ADDRESS"):
            availability["temporal"] = True
    except ImportError:
        pass

    # Check Celery
    try:
        import celery  # noqa: F401

        availability["celery"] = True
    except ImportError:
        pass

    # Check Prefect
    try:
        import prefect  # noqa: F401

        availability["prefect"] = True
    except ImportError:
        pass

    # Check Airflow
    try:
        import airflow  # noqa: F401

        # F401: 'airflow' imported but unused (flake8)
        # Remove this import as it is not used
        # availability["airflow"] = True  # This line is not present, so nothing to set
    except ImportError:
        pass

    return availability


def get_orchestration_config() -> OrchestrationConfig:
    """Get orchestration configuration with smart defaults."""

    # Check what's available
    available = detect_available_orchestrators()

    # Default configuration
    config = OrchestrationConfig()

    # Auto-detect and configure if orchestrator is available
    if available["temporal"] and os.getenv("TEMPORAL_API_KEY"):
        config.enabled = True
        config.orchestrator_type = "temporal"
        config.temporal.update(
            {
                "namespace": os.getenv("TEMPORAL_NAMESPACE", "default"),
                "address": os.getenv("TEMPORAL_ADDRESS", "localhost:7233"),
                "tls_enabled": "cloud.temporal.io" in os.getenv("TEMPORAL_ADDRESS", ""),
            }
        )
        logger.info("\U0001f3ad Auto-detected Temporal.io orchestration")

    elif available["celery"]:
        # Could add auto-detection for Redis/RabbitMQ here
        logger.info("\U0001f527 Celery available but not auto-configured")

    elif available["prefect"]:
        logger.info("\U0001f30a Prefect available but not auto-configured")

    else:
        logger.info("\u26a1 Using standalone mode - no orchestrator detected")

    return config


# =============================================================================
# WORKFLOW INTEGRATION PATTERNS
# =============================================================================


class WorkflowContext(BaseModel):
    """Context for workflow integration and orchestration."""

    # Workflow identification
    workflow_id: str = Field(default_factory=lambda: str(uuid4()))
    parent_workflow_id: str | None = None
    step_name: str = "ai_linting"

    # Execution context
    execution_mode: str = "standalone"  # standalone, orchestrated, pipeline
    priority: int = 5  # 1-10, higher = more priority
    timeout_seconds: int = 300
    retry_config: dict[str, Any] = Field(
        default_factory=lambda: {"max_retries": 3, "retry_delay": 1.0, "exponential_backoff": True}
    )

    # Resource management
    resource_requirements: dict[str, Any] = Field(
        default_factory=lambda: {
            "cpu_cores": 4,
            "memory_mb": 1024,
            "api_quota": 100,
            "estimated_duration": 60,
        }
    )

    # Integration hooks
    progress_callback: Callable | None = None
    error_callback: Callable | None = None
    completion_callback: Callable | None = None

    # Workflow dependencies
    depends_on: list[str] = Field(default_factory=list)
    triggers: list[str] = Field(default_factory=list)

    # Metadata for orchestration
    metadata: dict[str, Any] = Field(default_factory=dict)

    class Config:
        arbitrary_types_allowed = True

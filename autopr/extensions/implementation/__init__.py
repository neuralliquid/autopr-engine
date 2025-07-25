"""
Implementation Roadmap Package

Modular implementation system for AutoPR extension roadmap.
"""

from .task_definitions import Task, TaskRegistry
from .task_executor import TaskExecutor, TaskExecution
from .phase_manager import PhaseManager, PhaseExecution
from .report_generator import ReportGenerator
from .implementor import Phase1ExtensionImplementor

__all__ = [
    "Task",
    "TaskRegistry",
    "TaskExecutor",
    "TaskExecution",
    "PhaseManager",
    "PhaseExecution",
    "ReportGenerator",
    "Phase1ExtensionImplementor",
]

__version__ = "1.0.0"

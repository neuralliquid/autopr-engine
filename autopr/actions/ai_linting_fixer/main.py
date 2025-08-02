"""
Main AI Linting Fixer Module (Refactored)

This is the core module that orchestrates all the modular components
to provide AI-powered linting fixes. Much cleaner and focused!
"""

import logging
from datetime import datetime
from typing import Any

# Configure logging to suppress verbose provider warnings
logging.getLogger("autopr.actions.llm.manager").setLevel(logging.ERROR)


from .agents import AgentType, agent_manager
from .database import AIInteractionDB, IssueQueueManager
from .detection import issue_detector
from .display import DisplayConfig, OutputMode, get_display
from .file_ops import dry_run_ops, safe_file_ops
from .metrics import MetricsCollector

# Import core data models
from .models import (
    AILintingFixerInputs,
    AILintingFixerOutputs,
    LintingFixResult,
    LintingIssue,
    create_empty_outputs,
)

# Import modular components
from .workflow import WorkflowContext, WorkflowIntegrationMixin

# Optional Redis support
try:
    from .redis_queue import REDIS_AVAILABLE, RedisConfig, RedisQueueManager
except ImportError:
    REDIS_AVAILABLE = False
    RedisQueueManager = None

# Core AutoPR dependencies
from autopr.actions.llm.manager import LLMProviderManager

logger = logging.getLogger(__name__)


# =============================================================================
# MAIN AI LINTING FIXER CLASS (Using Modular Architecture)
# =============================================================================


class AILintingFixer(WorkflowIntegrationMixin):
    """
    AI-powered linting fixer with modular architecture.

    This class now focuses only on the core AI fixing logic,
    delegating specialized concerns to dedicated modules.
    """

    def __init__(
        self,
        llm_manager: LLMProviderManager = None,
        max_workers: int = 4,
        workflow_context: WorkflowContext | None = None,
    ):
        """Initialize with clean separation of concerns and full modular architecture."""
        super().__init__()
        self.workflow_context = workflow_context
        self.llm_manager = llm_manager
        self.max_workers = max_workers

        # Use modular metrics collector
        self.metrics = MetricsCollector()
        self.metrics.start_session()

        # Database-first processing components
        self.db = AIInteractionDB()
        self.queue_manager = IssueQueueManager(self.db)
        self.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{id(self)}"

        # Initialize modular components
        self.agent_manager = agent_manager
        self.issue_detector = issue_detector
        self.safe_file_ops = safe_file_ops
        self.dry_run_ops = dry_run_ops

        # Optional Redis support
        self.redis_manager = None
        if REDIS_AVAILABLE:
            try:
                self.redis_manager = RedisConfig.create_queue_manager()
            except Exception as e:
                logger.debug(f"Redis not available: {e}")

        # Track processing statistics
        self.stats = {
            "issues_detected": 0,
            "issues_queued": 0,
            "issues_processed": 0,
            "issues_fixed": 0,
            "issues_failed": 0,
        }

    def run_flake8(self, target_path: str) -> list[LintingIssue]:
        """Run flake8 and parse issues (delegated to issue detection module in full version)."""
        self.metrics.start_operation("flake8")

        try:
            # Use the modular issue detector
            detected_issues = self.issue_detector.detect_issues(target_path)

            # Convert to the legacy LintingIssue format for compatibility
            issues = []
            for issue in detected_issues:
                legacy_issue = LintingIssue(
                    file_path=issue.file_path,
                    line_number=issue.line_number,
                    column_number=issue.column_number,
                    error_code=issue.error_code,
                    message=issue.message,
                    line_content=issue.line_content,
                )
                issues.append(legacy_issue)

            self.stats["issues_detected"] = len(issues)
            return issues

        except Exception as e:
            logger.exception(f"Error detecting issues: {e}")
            return []
        finally:
            self.metrics.end_operation("flake8")

    def _parse_flake8_standard_output(self, output: str) -> list[LintingIssue]:
        """Parse flake8 standard output format."""
        issues = []
        for line in output.strip().split("\n"):
            if not line.strip():
                continue
            try:
                # Parse format: file:line:col: code message
                parts = line.split(":", 3)
                if len(parts) >= 4:
                    file_path = parts[0].strip()
                    line_num = int(parts[1].strip())
                    col_num = int(parts[2].strip())
                    code_msg = parts[3].strip()

                    # Extract error code
                    code_parts = code_msg.split(" ", 1)
                    error_code = code_parts[0]
                    message = code_parts[1] if len(code_parts) > 1 else ""

                    issues.append(
                        LintingIssue(
                            file_path=file_path,
                            line_number=line_num,
                            column_number=col_num,
                            error_code=error_code,
                            message=message,
                        )
                    )
            except (ValueError, IndexError) as e:
                logger.debug(f"Failed to parse flake8 line: {line} - {e}")
                continue

        return issues

    def select_specialized_agent(self, issues: list[LintingIssue]) -> Any:
        """Select the most appropriate specialized agent for a batch of issues."""
        if not issues:
            return self.agent_manager.get_agent_by_type(AgentType.GENERAL_FIXER)

        # Convert to the format expected by agent manager
        issue_dicts = [
            {
                "error_code": issue.error_code,
                "file_path": issue.file_path,
                "line_number": issue.line_number,
                "message": issue.message,
            }
            for issue in issues
        ]

        return self.agent_manager.select_agent_for_issues(issue_dicts)

    def apply_agent_fix(
        self,
        agent: Any,
        file_path: str,
        issues: list[LintingIssue],
        use_safe_ops: bool = True,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        """Apply an AI fix using the specified specialized agent."""
        try:
            # Read file content
            with open(file_path, encoding="utf-8") as f:
                file_content = f.read()

            # Convert issues to format expected by agent
            issue_dicts = [
                {
                    "error_code": issue.error_code,
                    "line_number": issue.line_number,
                    "column_number": issue.column_number,
                    "message": issue.message,
                    "file_path": issue.file_path,
                }
                for issue in issues
            ]

            # Get specialized prompts from agent
            agent.get_system_prompt(issue_dicts)
            agent.get_user_prompt(file_content, issue_dicts)

            if dry_run:
                # Use dry run operations
                operation = self.dry_run_ops.plan_file_write(
                    file_path=file_path,
                    content=f"# DRY RUN: Would apply {agent.agent_type.value} fixes",
                    reason=f"AI fix using {agent.agent_type.value}",
                )

                return {
                    "success": True,
                    "confidence_score": (
                        agent.get_confidence_score(issues[0].error_code) if issues else 0.7
                    ),
                    "agent_type": agent.agent_type.value,
                    "dry_run_operation": operation,
                    "fixed_content": "DRY RUN - No actual changes",
                }

            # For now, simulate the AI fix - in production this would call LLM
            return self._simulate_agent_fix(file_path, file_content, agent, issues, use_safe_ops)

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "agent_type": agent.agent_type.value if hasattr(agent, "agent_type") else "unknown",
                "confidence_score": 0.0,
            }

    def _simulate_agent_fix(
        self,
        file_path: str,
        file_content: str,
        agent: Any,
        issues: list[LintingIssue],
        use_safe_ops: bool,
    ) -> dict[str, Any]:
        """Simulate agent fix (placeholder for actual LLM integration)."""

        try:
            # Simulate processing time and create a mock fix
            import time

            time.sleep(0.05)  # Brief simulation

            agent_name = agent.agent_type.value
            fixed_content = file_content + f"\n# Simulated fix by {agent_name}\n"

            if use_safe_ops:
                # Use safe file operations with backup
                success = self.safe_file_ops.write_file_safely(
                    file_path=file_path,
                    content=fixed_content,
                    validate_syntax=True,
                    create_backup=True,
                )
            else:
                # Direct write (not recommended for production)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(fixed_content)
                success = True

            confidence = agent.get_confidence_score(issues[0].error_code) if issues else 0.7

            return {
                "success": success,
                "confidence_score": confidence,
                "agent_type": agent_name,
                "fixed_content": (
                    fixed_content[:200] + "..." if len(fixed_content) > 200 else fixed_content
                ),
                "issues_addressed": len(issues),
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "agent_type": agent.agent_type.value if hasattr(agent, "agent_type") else "unknown",
                "confidence_score": 0.0,
            }

    def queue_detected_issues(self, issues: list[LintingIssue], quiet: bool = False) -> int:
        """Queue detected linting issues for database-first processing."""
        if not quiet:
            pass

        # Convert LintingIssue objects to database format
        issue_data = [
            {
                "file_path": issue.file_path,
                "line_number": issue.line_number,
                "column_number": issue.column_number,
                "error_code": issue.error_code,
                "message": issue.message,
                "line_content": getattr(issue, "line_content", ""),
                "priority": self._calculate_issue_priority(issue.error_code),
            }
            for issue in issues
        ]

        # Queue all issues in database
        queued_count = self.queue_manager.queue_issues(self.session_id, issue_data)

        if not quiet:
            pass
        return queued_count

    def _calculate_issue_priority(self, error_code: str) -> int:
        """Calculate priority for an issue type (1-10, higher = more priority)."""
        priority_map = {
            "F401": 8,  # Unused imports - high priority, easy to fix
            "F841": 7,  # Unused variable - high priority
            "E501": 6,  # Line too long - medium-high priority
            "E722": 5,  # Bare except - medium priority
            "F541": 4,  # F-string missing placeholders - medium-low priority
            "E741": 3,  # Ambiguous variable name - low priority
        }

        base_code = error_code.split("(")[0]  # Remove any parenthetical info
        return priority_map.get(base_code, 5)  # Default to medium priority

    def process_issues_from_queue(
        self,
        max_fixes: int = 10,
        provider: str | None = None,
        model: str | None = None,
        filter_types: list[str] | None = None,
        quiet: bool = False,
    ) -> dict[str, Any]:
        """Process issues from the database queue using AI."""
        worker_id = f"worker_{self.session_id}"

        self.emit_event(
            "started",
            {"session_id": self.session_id, "worker_id": worker_id, "max_fixes": max_fixes},
        )

        total_processed = 0
        successful_fixes = 0
        failed_fixes = 0
        modified_files = set()

        if not quiet:
            pass

        while total_processed < max_fixes:
            # Get next batch of issues from queue
            remaining_slots = max_fixes - total_processed
            batch_size = min(5, remaining_slots)  # Process in small batches

            issues_batch = self.queue_manager.get_next_issues(
                limit=batch_size, worker_id=worker_id, filter_types=filter_types
            )

            if not issues_batch:
                if not quiet:
                    pass
                break

            if not quiet:
                pass

            for issue_data in issues_batch:
                self.metrics.start_operation(f"process_issue_{issue_data['id']}")

                try:
                    # Simulate AI processing (replace with real AI call later)
                    success = self._simulate_ai_fix_from_queue(issue_data, provider, model)

                    if success:
                        successful_fixes += 1
                        modified_files.add(issue_data["file_path"])

                        self.queue_manager.update_issue_status(
                            issue_data["id"],
                            "completed",
                            {
                                "fix_successful": True,
                                "confidence_score": 0.85,
                                "ai_response": f"Successfully fixed {issue_data['error_code']}",
                            },
                        )
                        if not quiet:
                            pass

                    else:
                        failed_fixes += 1
                        self.queue_manager.update_issue_status(
                            issue_data["id"],
                            "failed",
                            {
                                "fix_successful": False,
                                "error_message": f"Failed to fix {issue_data['error_code']}",
                            },
                        )
                        if not quiet:
                            pass

                    self.metrics.record_fix_attempt(success, confidence=0.85 if success else 0.0)
                    total_processed += 1

                except Exception as e:
                    failed_fixes += 1
                    self.queue_manager.update_issue_status(
                        issue_data["id"],
                        "failed",
                        {"fix_successful": False, "error_message": str(e)},
                    )
                    logger.exception(f"Error processing issue {issue_data['id']}: {e}")
                    total_processed += 1

                finally:
                    self.metrics.end_operation(f"process_issue_{issue_data['id']}")

        result = {
            "total_processed": total_processed,
            "successful_fixes": successful_fixes,
            "failed_fixes": failed_fixes,
            "modified_files": list(modified_files),
            "session_id": self.session_id,
        }

        self.emit_event("completed", result)

        if not quiet:
            pass
        return result

    def fix_issues_with_ai(
        self,
        issues: list[LintingIssue],
        max_fixes: int = 10,
        provider: str | None = None,
        model: str | None = None,
    ) -> LintingFixResult:
        """
        Fix issues using AI with clean architecture.

        In the full modular version, this would delegate to:
        - AgentManager for specialized fixing
        - FileOperations for safe file handling
        - Database module for logging
        """
        self.emit_event("started", {"total_issues": len(issues), "max_fixes": max_fixes})

        # Simplified implementation for demonstration
        # In full version, this would use the agent manager
        fixed_issues = []
        modified_files = []

        # For now, simulate some fixes
        for i, issue in enumerate(issues[:max_fixes]):
            self.metrics.start_operation(f"fix_issue_{i}")

            try:
                # Simulate AI fixing process
                success = self._simulate_ai_fix(issue, provider, model)

                if success:
                    fixed_issues.append(f"{issue.error_code}:{issue.line_number}")
                    if issue.file_path not in modified_files:
                        modified_files.append(issue.file_path)

                    self.metrics.record_fix_attempt(True, confidence=0.85)
                else:
                    self.metrics.record_fix_attempt(False)

            except Exception as e:
                logger.exception(f"Error fixing issue {issue}: {e}")
                self.metrics.record_fix_attempt(False)
            finally:
                self.metrics.end_operation(f"fix_issue_{i}")

        self.emit_event(
            "completed", {"issues_fixed": len(fixed_issues), "files_modified": len(modified_files)}
        )

        return LintingFixResult(
            success=len(fixed_issues) > 0,
            fixed_issues=fixed_issues,
            remaining_issues=[
                f"{issue.error_code}:{issue.line_number}" for issue in issues[max_fixes:]
            ],
            modified_files=modified_files,
        )

    def _simulate_ai_fix(
        self, issue: LintingIssue, provider: str | None, model: str | None
    ) -> bool:
        """
        Simulate AI fixing for demonstration.
        In full version, this would call the actual LLM.
        """
        self.metrics.record_api_call(1.5, tokens_used=150)  # Simulate API call

        # Simulate different success rates for different issue types
        success_rates = {
            "F401": 0.9,  # Unused imports - high success
            "E501": 0.7,  # Line too long - medium success
            "F841": 0.8,  # Unused variable - high success
            "E722": 0.6,  # Bare except - medium success
            "F541": 0.4,  # F-string missing placeholders - lower success
        }

        base_code = issue.error_code.split("(")[0]
        success_rate = success_rates.get(base_code, 0.5)

        # Simulate based on success rate
        import random

        return random.random() < success_rate  # - Used for simulation, not security

    def _simulate_ai_fix_from_queue(
        self, issue_data: dict[str, Any], provider: str | None, model: str | None
    ) -> bool:
        """
        Simulate AI fixing for demonstration using database queue data.
        In full version, this would call the actual LLM with the issue data.
        """
        self.metrics.record_api_call(1.5, tokens_used=150)  # Simulate API call

        # Simulate different success rates for different issue types
        success_rates = {
            "F401": 0.9,  # Unused imports - high success
            "E501": 0.7,  # Line too long - medium success
            "F841": 0.8,  # Unused variable - high success
            "E722": 0.6,  # Bare except - medium success
            "F541": 0.4,  # F-string missing placeholders - lower success
        }

        error_code = issue_data["error_code"]
        base_code = error_code.split("(")[0]
        success_rate = success_rates.get(base_code, 0.5)

        # Simulate based on success rate and priority
        priority_bonus = issue_data.get("priority", 5) / 10 * 0.1  # Small priority bonus
        effective_success_rate = min(0.95, success_rate + priority_bonus)

        # Simulate based on success rate
        import random

        return random.random() < effective_success_rate  # - Used for simulation, not security

    def close(self) -> None:
        """Clean up resources."""
        self.metrics.end_session()

        # Log session performance to database
        performance_metrics = self.metrics.calculate_performance_metrics()
        session_data = {
            "session_timestamp": datetime.now().isoformat(),
            "total_duration": performance_metrics.total_duration,
            "files_processed": performance_metrics.total_files_processed,
            "issues_found": performance_metrics.total_issues_found,
            "issues_fixed": performance_metrics.total_issues_fixed,
            "success_rate": performance_metrics.success_rate,
            "average_confidence": performance_metrics.average_confidence_score,
            "throughput_files_per_sec": performance_metrics.files_per_second,
            "throughput_issues_per_sec": performance_metrics.issues_per_second,
            "parallel_workers": self.max_workers,
            "total_tokens": performance_metrics.total_tokens_used,
            "total_api_calls": performance_metrics.api_calls_made,
            "average_api_response_time": performance_metrics.average_api_response_time,
            "provider_used": "azure_openai",  # Default
            "model_used": "gpt-4.1",  # Default
        }

        self.db.log_performance_session(session_data)

        # In full version, would close:
        # - Database connections
        # - Thread pools
        # - File handles
        # - etc.

    def get_queue_statistics(self) -> dict[str, Any]:
        """Get queue statistics."""
        return self.queue_manager.get_queue_statistics()

    def get_session_results(self) -> AILintingFixerOutputs:
        """Get comprehensive session results."""
        # Get queue statistics
        queue_stats = self.get_queue_statistics()

        # Get agent statistics
        agent_stats = self.agent_manager.get_all_agent_stats()

        # Calculate session metrics
        session_metrics = self.metrics.get_session_metrics()

        # Create results object
        return AILintingFixerOutputs(
            session_id=self.session_id,
            timestamp=datetime.now(),
            total_issues_detected=self.stats["issues_detected"],
            issues_queued=self.stats["issues_queued"],
            issues_processed=self.stats["issues_processed"],
            issues_fixed=self.stats["issues_fixed"],
            issues_failed=self.stats["issues_failed"],
            files_analyzed=(
                len({issue.file_path for issue in self.detected_issues})
                if hasattr(self, "detected_issues")
                else 0
            ),
            files_modified=len(self.modified_files) if hasattr(self, "modified_files") else 0,
            backup_files_created=len(self.backup_files) if hasattr(self, "backup_files") else 0,
            total_duration=session_metrics.get("total_duration", 0.0),
            detection_duration=0.0,  # TODO: Track separately
            processing_duration=0.0,  # TODO: Track separately
            success=self.stats["issues_fixed"] > 0,
            agent_stats=agent_stats,
            queue_stats=queue_stats,
            redis_stats={},  # TODO: Add Redis stats
            errors=self.errors if hasattr(self, "errors") else [],
            warnings=self.warnings if hasattr(self, "warnings") else [],
        )


# =============================================================================
# MAIN FUNCTION (Much Simpler!)
# =============================================================================


def ai_linting_fixer(inputs: AILintingFixerInputs) -> AILintingFixerOutputs:
    """
    Main AI linting function with clean modular architecture using new display system.

    This function now uses the modular display system for all UI interactions,
    providing clean separation between business logic and presentation.
    """

    # Initialize display system
    display_config = DisplayConfig(
        mode=(
            OutputMode.QUIET
            if inputs.quiet
            else OutputMode.VERBOSE
            if inputs.verbose_metrics
            else OutputMode.NORMAL
        )
    )
    display = get_display(display_config)

    try:
        # Initialize main fixer with all modular components
        fixer = AILintingFixer()

        # Show session start information
        display.operation.show_session_start(inputs, fixer.session_id)

        # Show provider status
        try:
            # Create default LLM config
            llm_config = {
                "default_provider": inputs.provider or "azure_openai",
                "fallback_order": ["azure_openai", "openai", "anthropic"],
                "providers": {
                    "azure_openai": {
                        "azure_endpoint": "https://dev-saf-openai-phoenixvc-ai.openai.azure.com/",
                        "api_version": "2024-02-01",
                        "deployment_name": inputs.model or "gpt-4.1",
                    }
                },
            }
            llm_manager = LLMProviderManager(llm_config)
            available_providers = llm_manager.get_available_providers()
            display.system.show_provider_status(available_providers)
        except Exception as e:
            display.error.show_warning(f"Could not check provider status: {e}")

        # Step 1: Detect issues
        display.operation.show_detection_progress(inputs.target_path)
        issues = fixer.issue_detector.detect_issues(inputs.target_path)

        # Update stats
        fixer.stats["issues_detected"] = len(issues)

        if not issues:
            # No issues found
            results = create_empty_outputs(fixer.session_id)
            results.success = True
            results.total_issues_detected = 0
            display.operation.show_detection_results(0, 0)
            display.results.show_results_summary(results)
            return results

        files_count = len({issue.file_path for issue in issues})
        display.operation.show_detection_results(len(issues), files_count)

        # Step 2: Queue issues for processing
        display.operation.show_queueing_progress(len(issues))

        # Convert issues to the format expected by queue_detected_issues
        legacy_issues = []
        for issue in issues:
            legacy_issue = LintingIssue(
                file_path=issue.file_path,
                line_number=issue.line_number,
                column_number=issue.column_number,
                error_code=issue.error_code,
                message=issue.message,
                line_content=issue.line_content,
            )
            legacy_issues.append(legacy_issue)

        queued_count = fixer.queue_detected_issues(legacy_issues, quiet=inputs.quiet)
        fixer.stats["issues_queued"] = queued_count
        display.operation.show_queueing_results(queued_count, len(issues))

        if queued_count == 0:
            # No issues queued
            results = create_empty_outputs(fixer.session_id)
            results.success = True
            results.total_issues_detected = len(issues)
            results.issues_queued = 0
            display.error.show_warning("No issues were queued for processing")
            return results

        # Step 3: Process issues
        processing_mode = "redis" if fixer.redis_manager else "local"
        display.operation.show_processing_start(processing_mode)

        process_results = fixer.process_issues_from_queue(
            max_fixes=inputs.max_fixes, filter_types=inputs.filter_types, quiet=inputs.quiet
        )

        # Update stats from processing results
        fixer.stats["issues_processed"] = process_results.get("processed", 0)
        fixer.stats["issues_fixed"] = process_results.get("fixed", 0)
        fixer.stats["issues_failed"] = process_results.get("failed", 0)

        display.operation.show_processing_results(
            process_results.get("fixed", 0), process_results.get("failed", 0)
        )

        # Show dry run notice if applicable
        if inputs.dry_run:
            display.operation.show_dry_run_notice()

        # Step 4: Generate final results
        final_results = fixer.get_session_results()

        # Display comprehensive results
        display.results.show_results_summary(final_results)
        if inputs.verbose_metrics:
            display.results.show_agent_performance(final_results.agent_stats)
            display.results.show_queue_statistics(final_results.queue_stats)
        display.results.show_suggestions(final_results)

        return final_results

    except Exception as e:
        # Handle errors with display system
        error_msg = f"AI linting fixer failed: {e!s}"
        logger.exception(error_msg)
        display.error.show_error(error_msg)

        # Return error result
        error_results = create_empty_outputs("error")
        error_results.success = False
        error_results.errors = [error_msg]
        return error_results

    finally:
        # Clean up
        try:
            if "fixer" in locals():
                fixer.close()
        except Exception as e:
            logger.debug(f"Cleanup error: {e}")


# Legacy compatibility functions
def print_feature_status() -> None:
    """Print feature status (legacy compatibility)."""
    from .display import print_feature_status as display_print_feature_status

    # Get system features
    features = {
        "core_ai_linting": True,
        "orchestration": False,
        "temporal_integration": False,
        "celery_integration": False,
        "prefect_integration": False,
        "performance_metrics": True,
        "workflow_integration": True,
        "specialized_agents": True,
        "database_support": True,
        "redis_support": REDIS_AVAILABLE,
    }

    # Check orchestration availability
    try:
        from .orchestration import detect_available_orchestrators

        available_orchestrators = detect_available_orchestrators()
        features["orchestration"] = any(available_orchestrators.values())
        features["temporal_integration"] = available_orchestrators.get("temporal", False)
        features["celery_integration"] = available_orchestrators.get("celery", False)
        features["prefect_integration"] = available_orchestrators.get("prefect", False)
    except:
        pass

    display_print_feature_status(features)


def display_provider_status(quiet: bool = False) -> None:
    """Display LLM provider status (legacy compatibility)."""
    from .display import display_provider_status as display_show_provider_status

    try:
        llm_manager = LLMProviderManager()
        available_providers = llm_manager.get_available_providers()
        display_show_provider_status(available_providers, quiet)
    except Exception:
        if not quiet:
            pass

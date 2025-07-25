#!/usr/bin/env python3
"""
AutoPR Integration: Axolo Communication Hub
Seamless GitHub ↔ Slack integration with ephemeral PR channels
"""

import os
import asyncio
import aiohttp
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import structlog
from dataclasses import dataclass

logger = structlog.get_logger()


@dataclass
class AxoloPRChannel:
    channel_id: str
    channel_name: str
    pr_number: int
    repository: str
    created_at: datetime
    participants: List[str]
    status: str  # 'active', 'archived', 'closed'


@dataclass
class AxoloConfiguration:
    workspace_url: str
    slack_webhook: str
    github_repos: List[str]
    reminder_schedule: Dict[str, str]
    ai_tool_mentions: Dict[str, str]
    custom_commands: Dict[str, str]


class AxoloIntegration:
    """
    Primary communication integration using Axolo for GitHub ↔ Slack

    Features:
    - Ephemeral PR channels (1 PR = 1 Channel)
    - Bi-directional GitHub/Slack sync
    - AI tool integration and mentions
    - Custom AutoPR commands
    - Smart reminder system
    """

    def __init__(self) -> None:
        self.config = self._load_configuration()
        self.active_channels: Dict[str, AxoloPRChannel] = {}
        self.session: Optional[aiohttp.ClientSession] = None

        # Integration clients
        self.github_client = None
        self.slack_client = None
        self.linear_client = None

    def _load_configuration(self) -> AxoloConfiguration:
        """Load Axolo configuration from environment"""

        return AxoloConfiguration(
            workspace_url=os.getenv("AXOLO_WORKSPACE_URL", ""),
            slack_webhook=os.getenv("AXOLO_SLACK_WEBHOOK", ""),
            github_repos=os.getenv("AXOLO_GITHUB_REPOS", "").split(","),
            reminder_schedule={
                "daily_standup": os.getenv("AXOLO_STANDUP_TIME", "09:00"),
                "stale_pr_reminder": os.getenv("AXOLO_STALE_REMINDER", "14:00"),
                "end_of_day_summary": os.getenv("AXOLO_EOD_SUMMARY", "17:00"),
            },
            ai_tool_mentions={
                "@autopr": "Triggers comprehensive AutoPR analysis",
                "@coderabbit": "Requests CodeRabbit code review",
                "@copilot": "Activates GitHub Copilot assistance",
                "@linear": "Creates Linear issue from discussion",
                "@security": "Runs security analysis on PR",
            },
            custom_commands={
                "/autopr-analyze": "analyze_pr_command",
                "/autopr-status": "pr_status_command",
                "/autopr-assign-ai": "assign_ai_command",
                "/autopr-create-issues": "create_issues_command",
                "/autopr-platform-detect": "platform_detect_command",
            },
        )

    async def initialize(self):
        """Initialize Axolo integration and dependencies"""

        logger.info("Initializing Axolo integration")

        # Create HTTP session
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30))

        # Initialize dependent clients
        await self._initialize_clients()

        # Setup Axolo configuration
        await self._setup_axolo_integration()

        # Register custom commands
        await self._register_custom_commands()

        # Start background tasks
        asyncio.create_task(self._background_reminder_service())

        logger.info("Axolo integration initialized successfully")

    async def _initialize_clients(self):
        """Initialize GitHub, Slack, and Linear clients"""

        try:
            # GitHub client
            from tools.autopr.clients.github_client import GitHubClient

            self.github_client = GitHubClient(os.getenv("GITHUB_TOKEN"))

            # Slack client (if using direct API)
            from slack_sdk.web.async_client import AsyncWebClient

            self.slack_client = AsyncWebClient(token=os.getenv("SLACK_BOT_TOKEN"))

            # Linear client
            from tools.autopr.clients.linear_client import LinearClient

            self.linear_client = LinearClient(os.getenv("LINEAR_API_KEY"))

            logger.info("Integration clients initialized")

        except Exception as e:
            logger.error("Failed to initialize clients", error=str(e))
            raise

    async def _setup_axolo_integration(self):
        """Configure Axolo for AutoPR workflow"""

        logger.info("Configuring Axolo for AutoPR repositories")

        for repo in self.config.github_repos:
            if not repo.strip():
                continue

            await self._configure_repository_integration(repo.strip())

        # Setup AI tool notification routing
        await self._setup_ai_tool_notifications()

        # Configure reminder schedules
        await self._setup_reminder_schedules()

        logger.info("Axolo configuration complete")

    async def _configure_repository_integration(self, repository: str):
        """Configure Axolo for specific repository"""

        config = {
            "repository": repository,
            "settings": {
                "auto_invite_reviewers": True,
                "auto_invite_assignees": True,
                "ci_cd_notifications": True,
                "deployment_notifications": True,
                "github_actions_notifications": True,
                "archive_on_merge": True,
                "archive_on_close": True,
                "thread_code_comments": True,
                "sync_slack_github": True,
            },
            "review_time_slots": {
                "morning_slot": "09:00-11:00",
                "afternoon_slot": "14:00-16:00",
                "timezone": os.getenv("TEAM_TIMEZONE", "UTC"),
            },
            "notification_filters": {
                "include_draft_prs": False,
                "include_bot_prs": True,  # Include our AutoPR bot PRs
                "minimum_pr_size": 1,  # Lines changed
                "excluded_branches": ["dependabot/*", "renovate/*"],
            },
        }

        # Apply configuration via Axolo API (if available)
        await self._apply_axolo_repository_config(repository, config)

        logger.info("Repository configured for Axolo", repository=repository)

    async def _setup_ai_tool_notifications(self):
        """Setup AI tool integration with Axolo channels"""

        ai_config = {
            "mention_triggers": self.config.ai_tool_mentions,
            "auto_responses": {
                "@autopr": "AutoPR analysis initiated. Results will be posted here.",
                "@coderabbit": "CodeRabbit review requested. Analysis in progress.",
                "@copilot": "GitHub Copilot activated for this PR.",
                "@linear": "Creating Linear issue from this discussion.",
                "@security": "Security scan initiated for this PR.",
            },
            "webhook_endpoints": {
                "autopr_complete": f"{os.getenv('AUTOPR_WEBHOOK_BASE')}/axolo/analysis/complete",
                "ai_tool_response": f"{os.getenv('AUTOPR_WEBHOOK_BASE')}/axolo/ai/response",
            },
        }

        await self._configure_ai_integrations(ai_config)

        logger.info("AI tool notifications configured")

    async def _register_custom_commands(self):
        """Register custom Slack commands for AutoPR"""

        commands = {
            "/autopr-analyze": {
                "description": "Trigger comprehensive AutoPR analysis",
                "handler": self._handle_analyze_command,
                "usage": "/autopr-analyze [pr_url]",
            },
            "/autopr-status": {
                "description": "Show AutoPR analysis status",
                "handler": self._handle_status_command,
                "usage": "/autopr-status",
            },
            "/autopr-assign-ai": {
                "description": "Assign AI tool to current PR",
                "handler": self._handle_assign_ai_command,
                "usage": "/autopr-assign-ai <tool_name>",
            },
            "/autopr-create-issues": {
                "description": "Create Linear issues from analysis",
                "handler": self._handle_create_issues_command,
                "usage": "/autopr-create-issues",
            },
            "/autopr-platform-detect": {
                "description": "Run platform detection on PR",
                "handler": self._handle_platform_detect_command,
                "usage": "/autopr-platform-detect",
            },
        }

        for command, config in commands.items():
            await self._register_slack_command(command, config)

        logger.info("Custom commands registered", commands=list(commands.keys()))

    # ============================================================================
    # Core PR Channel Management
    # ============================================================================

    async def create_pr_channel(self, pr_data: Dict[str, Any]) -> AxoloPRChannel:
        """Create or get existing Axolo channel for PR"""

        pr_key = f"{pr_data['repository']}/#{pr_data['pr_number']}"

        # Check if channel already exists
        if pr_key in self.active_channels:
            return self.active_channels[pr_key]

        # Let Axolo create the channel (it does this automatically)
        # We just track it in our system
        channel = AxoloPRChannel(
            channel_id=f"pr-{pr_data['repository'].replace('/', '-')}-{pr_data['pr_number']}",
            channel_name=f"PR #{pr_data['pr_number']}: {pr_data['title'][:30]}...",
            pr_number=pr_data["pr_number"],
            repository=pr_data["repository"],
            created_at=datetime.utcnow(),
            participants=[],
            status="active",
        )

        self.active_channels[pr_key] = channel

        logger.info(
            "PR channel created",
            channel_id=channel.channel_id,
            pr_number=pr_data["pr_number"],
            repository=pr_data["repository"],
        )

        return channel

    async def post_autopr_analysis(
        self, channel: AxoloPRChannel, analysis_result: Dict[str, Any]
    ):
        """Post AutoPR analysis results to Axolo channel"""

        # Format analysis summary
        summary = self._format_analysis_summary(analysis_result)

        # Create rich Slack message
        message = {
            "channel": channel.channel_id,
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "🤖 AutoPR Analysis Complete",
                    },
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Platform Detected:*\n{analysis_result.get('platform_detected', 'Unknown')}",
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Confidence:*\n{analysis_result.get('confidence_score', 0):.0%}",
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Issues Found:*\n{len(analysis_result.get('issues_found', []))}",
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*AI Tools Assigned:*\n{len(analysis_result.get('ai_assignments', []))}",
                        },
                    ],
                },
            ],
        }

        # Add detailed findings if any
        if analysis_result.get("issues_found"):
            issues_block = self._create_issues_block(analysis_result["issues_found"])
            message["blocks"].append(issues_block)

        # Add next steps
        if analysis_result.get("next_steps"):
            next_steps_block = self._create_next_steps_block(
                analysis_result["next_steps"]
            )
            message["blocks"].append(next_steps_block)

        # Post to Slack
        await self._post_slack_message(message)

        logger.info(
            "Analysis posted to channel",
            channel_id=channel.channel_id,
            issues_count=len(analysis_result.get("issues_found", [])),
        )

    async def link_linear_issues(
        self, channel: AxoloPRChannel, issues: List[Dict[str, Any]]
    ):
        """Link created Linear issues to Axolo channel"""

        if not issues:
            return

        message = {
            "channel": channel.channel_id,
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"🎯 *{len(issues)} Linear Issues Created*",
                    },
                }
            ],
        }

        # Add each issue as a block
        for issue in issues:
            issue_block = {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"• <{issue['url']}|{issue['title']}>\n   Priority: {issue.get('priority', 'Medium')} | Assigned: {issue.get('assignee', 'Unassigned')}",
                },
            }
            message["blocks"].append(issue_block)

        await self._post_slack_message(message)

        logger.info(
            "Linear issues linked to channel",
            channel_id=channel.channel_id,
            issues_count=len(issues),
        )

    async def setup_ai_assignments(
        self, channel: AxoloPRChannel, assignments: List[Dict[str, Any]]
    ):
        """Setup AI tool assignments in channel"""

        if not assignments:
            return

        message = {
            "channel": channel.channel_id,
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "🤖 *AI Tools Assigned to this PR*",
                    },
                }
            ],
        }

        for assignment in assignments:
            ai_block = {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"• **{assignment['tool']}**: {assignment['task']}\n   Mention {assignment.get('mention', '@' + assignment['tool'])} to interact",
                },
            }
            message["blocks"].append(ai_block)

        await self._post_slack_message(message)

        logger.info(
            "AI assignments posted to channel",
            channel_id=channel.channel_id,
            assignments_count=len(assignments),
        )

    # ============================================================================
    # Command Handlers
    # ============================================================================

    async def _handle_analyze_command(self, command_data: Dict[str, Any]):
        """Handle /autopr-analyze command"""

        channel_id = command_data["channel_id"]
        user_id = command_data["user_id"]
        text = command_data.get("text", "")

        # Extract PR URL if provided, otherwise use current channel's PR
        pr_url = text.strip() if text.strip() else None

        if not pr_url:
            # Try to get PR from current channel context
            pr_data = await self._get_pr_from_channel_context(channel_id)
        else:
            # Parse PR from URL
            pr_data = await self._parse_pr_from_url(pr_url)

        if not pr_data:
            await self._post_error_response(
                channel_id,
                "Could not find PR to analyze. Please provide a PR URL or use this command in a PR channel.",
            )
            return

        # Trigger AutoPR analysis
        from tools.autopr.actions.pr_review_analyzer import PRReviewAnalyzer

        analyzer = PRReviewAnalyzer()

        # Post initial response
        await self._post_slack_response(
            channel_id, f"🤖 Starting AutoPR analysis for PR #{pr_data['pr_number']}..."
        )

        try:
            # Run analysis
            analysis_result = await analyzer.analyze_pr_review(
                {
                    "pr_number": pr_data["pr_number"],
                    "repository": pr_data["repository"],
                    "review_data": await self._gather_review_data(pr_data),
                }
            )

            # Get or create channel for this PR
            channel = await self.create_pr_channel(pr_data)

            # Post results
            await self.post_autopr_analysis(channel, analysis_result)

        except Exception as e:
            logger.error("Analysis command failed", error=str(e))
            await self._post_error_response(channel_id, f"Analysis failed: {str(e)}")

    async def _handle_status_command(self, command_data: Dict[str, Any]):
        """Handle /autopr-status command"""

        channel_id = command_data["channel_id"]

        # Get current channel's PR status
        pr_data = await self._get_pr_from_channel_context(channel_id)

        if not pr_data:
            await self._post_error_response(
                channel_id, "This command must be used in a PR channel."
            )
            return

        # Get status information
        status = await self._get_pr_analysis_status(pr_data)

        status_message = {
            "channel": channel_id,
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"📊 PR #{pr_data['pr_number']} Status",
                    },
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Repository:*\n{pr_data['repository']}",
                        },
                        {"type": "mrkdwn", "text": f"*Status:*\n{status['pr_status']}"},
                        {
                            "type": "mrkdwn",
                            "text": f"*Last Analysis:*\n{status.get('last_analysis', 'Never')}",
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Issues Count:*\n{status.get('issues_count', 0)}",
                        },
                    ],
                },
            ],
        }

        await self._post_slack_message(status_message)

    async def _handle_assign_ai_command(self, command_data: Dict[str, Any]):
        """Handle /autopr-assign-ai command"""

        channel_id = command_data["channel_id"]
        text = command_data.get("text", "").strip()

        if not text:
            await self._post_error_response(
                channel_id,
                "Please specify an AI tool: coderabbit, copilot, security, or autopr",
            )
            return

        ai_tool = text.lower()
        valid_tools = ["coderabbit", "copilot", "security", "autopr"]

        if ai_tool not in valid_tools:
            await self._post_error_response(
                channel_id, f"Unknown AI tool. Valid options: {', '.join(valid_tools)}"
            )
            return

        # Get PR context
        pr_data = await self._get_pr_from_channel_context(channel_id)

        if not pr_data:
            await self._post_error_response(
                channel_id, "This command must be used in a PR channel."
            )
            return

        # Assign AI tool
        await self._assign_ai_tool_to_pr(pr_data, ai_tool)

        await self._post_slack_response(
            channel_id, f"✅ {ai_tool.title()} assigned to PR #{pr_data['pr_number']}"
        )

    # ============================================================================
    # Background Services
    # ============================================================================

    async def _background_reminder_service(self):
        """Background service for PR reminders and updates"""

        while True:
            try:
                current_time = datetime.now().strftime("%H:%M")

                # Daily standup reminders
                if current_time == self.config.reminder_schedule["daily_standup"]:
                    await self._send_daily_standup_summary()

                # Stale PR reminders
                elif current_time == self.config.reminder_schedule["stale_pr_reminder"]:
                    await self._send_stale_pr_reminders()

                # End of day summary
                elif (
                    current_time == self.config.reminder_schedule["end_of_day_summary"]
                ):
                    await self._send_end_of_day_summary()

                # Sleep for 1 minute
                await asyncio.sleep(60)

            except Exception as e:
                logger.error("Background reminder service error", error=str(e))
                await asyncio.sleep(300)  # Wait 5 minutes on error

    async def _send_daily_standup_summary(self):
        """Send daily PR summary for standups"""

        summary = await self._generate_daily_pr_summary()

        if not summary["active_prs"]:
            return

        message = {
            "channel": os.getenv("SLACK_STANDUP_CHANNEL"),
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "📅 Daily PR Standup Summary",
                    },
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*{len(summary['active_prs'])} Active PRs* | *{len(summary['stale_prs'])} Need Review*",
                    },
                },
            ],
        }

        # Add PR details
        for pr in summary["active_prs"][:10]:  # Limit to 10 PRs
            pr_block = {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"• <{pr['url']}|#{pr['number']}: {pr['title'][:50]}>\n   Author: {pr['author']} | Status: {pr['status']}",
                },
            }
            message["blocks"].append(pr_block)

        await self._post_slack_message(message)

        logger.info(
            "Daily standup summary sent",
            active_prs=len(summary["active_prs"]),
            stale_prs=len(summary["stale_prs"]),
        )

    # ============================================================================
    # Utility Methods
    # ============================================================================

    def _format_analysis_summary(self, analysis_result: Dict[str, Any]) -> str:
        """Format AutoPR analysis results for Slack"""

        summary_parts = [
            f"**Platform Detected**: {analysis_result.get('platform_detected', 'Unknown')}",
            f"**Confidence Score**: {analysis_result.get('confidence_score', 0):.0%}",
            f"**Issues Found**: {len(analysis_result.get('issues_found', []))}",
            f"**AI Tools Assigned**: {len(analysis_result.get('ai_assignments', []))}",
        ]

        if (
            analysis_result.get("platform_detected")
            and analysis_result.get("confidence_score", 0) > 0.8
        ):
            summary_parts.append(
                f"**Recommendation**: High confidence detection - proceed with automated assignments"
            )

        return "\n".join(summary_parts)

    def _create_issues_block(self, issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create Slack block for issues found"""

        issues_text = []
        for issue in issues[:5]:  # Limit to 5 issues
            issues_text.append(
                f"• **{issue.get('severity', 'Medium')}**: {issue.get('title', 'Unknown Issue')}"
            )

        if len(issues) > 5:
            issues_text.append(f"... and {len(issues) - 5} more issues")

        return {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"**🔍 Issues Found:**\n" + "\n".join(issues_text),
            },
        }

    def _create_next_steps_block(self, next_steps: List[str]) -> Dict[str, Any]:
        """Create Slack block for next steps"""

        steps_text = []
        for i, step in enumerate(next_steps[:3], 1):
            steps_text.append(f"{i}. {step}")

        return {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"**📋 Next Steps:**\n" + "\n".join(steps_text),
            },
        }

    async def _post_slack_message(self, message: Dict[str, Any]):
        """Post message to Slack via Axolo or direct API"""

        try:
            if self.slack_client:
                await self.slack_client.chat_postMessage(**message)
            else:
                # Use webhook fallback
                async with self.session.post(
                    self.config.slack_webhook, json=message
                ) as response:
                    if response.status != 200:
                        logger.error(
                            "Failed to post Slack message", status=response.status
                        )

        except Exception as e:
            logger.error("Error posting Slack message", error=str(e))

    async def _post_slack_response(self, channel_id: str, text: str):
        """Post simple text response to Slack"""

        message = {"channel": channel_id, "text": text}

        await self._post_slack_message(message)

    async def _post_error_response(self, channel_id: str, error_text: str):
        """Post error response to Slack"""

        message = {"channel": channel_id, "text": f"❌ {error_text}"}

        await self._post_slack_message(message)

    async def cleanup(self):
        """Cleanup resources"""

        if self.session:
            await self.session.close()

        logger.info("Axolo integration cleaned up")


# ============================================================================
# Factory and Helper Functions
# ============================================================================


async def create_axolo_integration() -> AxoloIntegration:
    """Factory function to create and initialize Axolo integration"""

    integration = AxoloIntegration()
    await integration.initialize()
    return integration


def is_axolo_available() -> bool:
    """Check if Axolo integration is properly configured"""

    required_vars = ["AXOLO_WORKSPACE_URL", "SLACK_BOT_TOKEN", "GITHUB_TOKEN"]

    return all(os.getenv(var) for var in required_vars)


# Example usage and testing
if __name__ == "__main__":

    async def test_axolo_integration():
        """Test Axolo integration functionality"""

        if not is_axolo_available():
            print(
                "❌ Axolo integration not configured. Set required environment variables."
            )
            return

        print("🔧 Testing Axolo integration...")

        # Create integration
        axolo = await create_axolo_integration()

        # Test PR channel creation
        test_pr_data = {
            "pr_number": 123,
            "title": "Test PR for Axolo Integration",
            "repository": "test/repo",
            "author": "test-user",
            "html_url": "https://github.com/test/repo/pull/123",
        }

        channel = await axolo.create_pr_channel(test_pr_data)
        print(f"✅ PR Channel created: {channel.channel_id}")

        # Test analysis posting
        test_analysis = {
            "platform_detected": "Next.js",
            "confidence_score": 0.95,
            "issues_found": [
                {"severity": "High", "title": "Security vulnerability detected"},
                {"severity": "Medium", "title": "Performance optimization needed"},
            ],
            "ai_assignments": [
                {"tool": "CodeRabbit", "task": "Security review"},
                {"tool": "Copilot", "task": "Performance optimization"},
            ],
        }

        await axolo.post_autopr_analysis(channel, test_analysis)
        print("✅ Analysis posted to channel")

        # Cleanup
        await axolo.cleanup()
        print("✅ Axolo integration test complete")

    # Run test
    asyncio.run(test_axolo_integration())

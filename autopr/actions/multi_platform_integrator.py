"""
AutoPR Action: Multi-Platform Integrator
Integrates with various platforms for enhanced workflow coordination.
"""

import os
import json
import requests
from typing import Dict, Any, Optional, List, Union
from pydantic import BaseModel
from .base import Action


class MultiPlatformInputs(BaseModel):
    action_type: str  # "create_issue", "notify_team", "update_status"
    platform: str  # "linear", "slack", "discord", "notion", "jira"
    title: str
    description: str
    priority: str = "medium"
    assignee: Optional[str] = None
    team_id: Optional[str] = None
    labels: List[str] = []
    context_data: Dict[str, Any] = {}


class MultiPlatformOutputs(BaseModel):
    success: bool
    platform_id: Optional[str] = None
    platform_url: Optional[str] = None
    error_message: Optional[str] = None


class MultiPlatformIntegrator(Action[MultiPlatformInputs, MultiPlatformOutputs]):
    """Action for integrating with multiple platforms."""

    def __init__(self) -> None:
        super().__init__(
            name="multi_platform_integrator",
            description="Integrates with various platforms for enhanced workflow coordination",
            version="1.0.0",
        )

    async def execute(
        self, inputs: MultiPlatformInputs, context: Dict[str, Any]
    ) -> MultiPlatformOutputs:
        """Execute the multi-platform integration."""
        return integrate_multi_platform(inputs)


def integrate_multi_platform(inputs: MultiPlatformInputs) -> MultiPlatformOutputs:
    """
    Integrates with various platforms based on the specified action and platform.
    """

    if inputs.platform == "linear":
        return create_linear_issue(inputs)
    elif inputs.platform == "slack":
        return send_slack_notification(inputs)
    elif inputs.platform == "discord":
        return send_discord_message(inputs)
    elif inputs.platform == "notion":
        return create_notion_page(inputs)
    elif inputs.platform == "jira":
        return create_jira_ticket(inputs)
    else:
        return MultiPlatformOutputs(
            success=False, error_message=f"Unsupported platform: {inputs.platform}"
        )


def create_linear_issue(inputs: MultiPlatformInputs) -> MultiPlatformOutputs:
    """Create issue in Linear."""
    try:
        headers: Dict[str, str] = {
            "Authorization": f"Bearer {os.getenv('LINEAR_API_KEY')}",
            "Content-Type": "application/json",
        }

        # Map priority
        priority_map: Dict[str, int] = {"low": 4, "medium": 3, "high": 2, "critical": 1}

        mutation: str = """
        mutation IssueCreate($input: IssueCreateInput!) {
            issueCreate(input: $input) {
                success
                issue {
                    id
                    url
                    identifier
                }
            }
        }
        """

        variables: Dict[str, Any] = {
            "input": {
                "title": inputs.title,
                "description": inputs.description,
                "priority": priority_map.get(inputs.priority, 3),
                "teamId": inputs.team_id or os.getenv("LINEAR_TEAM_ID"),
                "labelIds": inputs.labels,
                "assigneeId": inputs.assignee,
            }
        }

        response: requests.Response = requests.post(
            "https://api.linear.app/graphql",
            headers=headers,
            json={"query": mutation, "variables": variables},
        )

        if response.status_code == 200:
            data: Dict[str, Any] = response.json()
            issue_data: Dict[str, Any] = data["data"]["issueCreate"]["issue"]
            return MultiPlatformOutputs(
                success=True,
                platform_id=issue_data["identifier"],
                platform_url=issue_data["url"],
            )
        else:
            return MultiPlatformOutputs(
                success=False, error_message=f"Linear API error: {response.status_code}"
            )
    except Exception as e:
        return MultiPlatformOutputs(success=False, error_message=str(e))


def send_slack_notification(inputs: MultiPlatformInputs) -> MultiPlatformOutputs:
    """Send notification to Slack."""
    try:
        webhook_url: str = os.getenv("SLACK_WEBHOOK_URL") or ""

        # Create rich Slack message
        message: Dict[str, Any] = {
            "text": f"🤖 AutoPR: {inputs.title}",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"🤖 AutoPR: {inputs.title}",
                    },
                },
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": inputs.description},
                },
                {
                    "type": "context",
                    "elements": [
                        {"type": "mrkdwn", "text": f"Priority: *{inputs.priority}*"},
                        {
                            "type": "mrkdwn",
                            "text": f"Labels: {', '.join(inputs.labels)}",
                        },
                    ],
                },
            ],
        }

        if inputs.context_data.get("pr_url"):
            message["blocks"].append(
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "View PR"},
                            "url": inputs.context_data["pr_url"],
                        }
                    ],
                }
            )

        response: requests.Response = requests.post(webhook_url, json=message)

        if response.status_code == 200:
            return MultiPlatformOutputs(
                success=True, platform_id="slack_message", platform_url=None
            )
        else:
            return MultiPlatformOutputs(
                success=False, error_message=f"Slack API error: {response.status_code}"
            )
    except Exception as e:
        return MultiPlatformOutputs(success=False, error_message=str(e))


def send_discord_message(inputs: MultiPlatformInputs) -> MultiPlatformOutputs:
    """Send message to Discord."""
    try:
        webhook_url: str = os.getenv("DISCORD_WEBHOOK_URL") or ""

        # Create Discord embed
        embed: Dict[str, Any] = {
            "title": f"🤖 AutoPR: {inputs.title}",
            "description": inputs.description,
            "color": 0x00FF00,  # Green
            "fields": [
                {"name": "Priority", "value": inputs.priority, "inline": True},
                {
                    "name": "Labels",
                    "value": ", ".join(inputs.labels) or "None",
                    "inline": True,
                },
            ],
        }

        if inputs.context_data.get("pr_url"):
            embed["url"] = inputs.context_data["pr_url"]

        message: Dict[str, Any] = {"embeds": [embed]}

        response: requests.Response = requests.post(webhook_url, json=message)

        if response.status_code == 204:
            return MultiPlatformOutputs(
                success=True, platform_id="discord_message", platform_url=None
            )
        else:
            return MultiPlatformOutputs(
                success=False,
                error_message=f"Discord API error: {response.status_code}",
            )
    except Exception as e:
        return MultiPlatformOutputs(success=False, error_message=str(e))


def create_notion_page(inputs: MultiPlatformInputs) -> MultiPlatformOutputs:
    """Create page in Notion."""
    try:
        headers: Dict[str, str] = {
            "Authorization": f"Bearer {os.getenv('NOTION_API_KEY') or ''}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28",
        }

        page_data: Dict[str, Any] = {
            "parent": {"database_id": os.getenv("NOTION_DATABASE_ID") or ""},
            "properties": {
                "Title": {"title": [{"text": {"content": inputs.title}}]},
                "Priority": {"select": {"name": inputs.priority}},
                "Status": {"select": {"name": "Todo"}},
                "Labels": {
                    "multi_select": [{"name": label} for label in inputs.labels]
                },
            },
            "children": [
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {"type": "text", "text": {"content": inputs.description}}
                        ]
                    },
                }
            ],
        }

        response: requests.Response = requests.post(
            "https://api.notion.com/v1/pages", headers=headers, json=page_data
        )

        if response.status_code == 200:
            data: Dict[str, Any] = response.json()
            return MultiPlatformOutputs(
                success=True, platform_id=data["id"], platform_url=data["url"]
            )
        else:
            return MultiPlatformOutputs(
                success=False, error_message=f"Notion API error: {response.status_code}"
            )
    except Exception as e:
        return MultiPlatformOutputs(success=False, error_message=str(e))


def create_jira_ticket(inputs: MultiPlatformInputs) -> MultiPlatformOutputs:
    """Create ticket in Jira."""
    try:
        auth: tuple = (os.getenv("JIRA_EMAIL") or "", os.getenv("JIRA_API_TOKEN") or "")

        # Map priority
        priority_map: Dict[str, Dict[str, str]] = {
            "low": {"name": "Low"},
            "medium": {"name": "Medium"},
            "high": {"name": "High"},
            "critical": {"name": "Highest"},
        }

        issue_data: Dict[str, Any] = {
            "fields": {
                "project": {"key": os.getenv("JIRA_PROJECT_KEY") or ""},
                "summary": inputs.title,
                "description": inputs.description,
                "issuetype": {"name": "Task"},
                "priority": priority_map.get(inputs.priority, {"name": "Medium"}),
                "labels": inputs.labels,
            }
        }

        if inputs.assignee:
            issue_data["fields"]["assignee"] = {"name": inputs.assignee}

        response: requests.Response = requests.post(
            f"{os.getenv('JIRA_BASE_URL') or ''}/rest/api/3/issue",
            auth=auth,
            json=issue_data,
            headers={"Content-Type": "application/json"},
        )

        if response.status_code == 201:
            data: Dict[str, Any] = response.json()
            return MultiPlatformOutputs(
                success=True,
                platform_id=data["key"],
                platform_url=f"{os.getenv('JIRA_BASE_URL') or ''}/browse/{data['key']}",
            )
        else:
            return MultiPlatformOutputs(
                success=False, error_message=f"Jira API error: {response.status_code}"
            )
    except Exception as e:
        return MultiPlatformOutputs(success=False, error_message=str(e))

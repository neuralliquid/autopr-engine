"""
AutoPR Action: Multi-Platform Integrator
Integrates with various platforms for enhanced workflow coordination.
"""

import os
import json
import requests
from typing import Dict, Any, Optional, List
from pydantic import BaseModel

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
            success=False,
            error_message=f"Unsupported platform: {inputs.platform}"
        )

def create_linear_issue(inputs: MultiPlatformInputs) -> MultiPlatformOutputs:
    """Create issue in Linear."""
    try:
        headers = {
            "Authorization": f"Bearer {os.getenv('LINEAR_API_KEY')}",
            "Content-Type": "application/json"
        }
        
        # Map priority
        priority_map = {"low": 4, "medium": 3, "high": 2, "critical": 1}
        
        mutation = """
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
        
        variables = {
            "input": {
                "title": inputs.title,
                "description": inputs.description,
                "priority": priority_map.get(inputs.priority, 3),
                "teamId": inputs.team_id or os.getenv('LINEAR_TEAM_ID'),
                "labelIds": inputs.labels,
                "assigneeId": inputs.assignee
            }
        }
        
        response = requests.post(
            "https://api.linear.app/graphql",
            headers=headers,
            json={"query": mutation, "variables": variables}
        )
        
        if response.status_code == 200:
            data = response.json()
            issue_data = data["data"]["issueCreate"]["issue"]
            return MultiPlatformOutputs(
                success=True,
                platform_id=issue_data["identifier"],
                platform_url=issue_data["url"]
            )
    except Exception as e:
        return MultiPlatformOutputs(success=False, error_message=str(e))

def send_slack_notification(inputs: MultiPlatformInputs) -> MultiPlatformOutputs:
    """Send notification to Slack."""
    try:
        webhook_url = os.getenv('SLACK_WEBHOOK_URL')
        
        # Create rich Slack message
        message = {
            "text": f"🤖 AutoPR: {inputs.title}",
            "blocks": [
                {
                    "type": "header",
                    "text": {"type": "plain_text", "text": f"🤖 AutoPR: {inputs.title}"}
                },
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": inputs.description}
                },
                {
                    "type": "context",
                    "elements": [
                        {"type": "mrkdwn", "text": f"Priority: *{inputs.priority}*"},
                        {"type": "mrkdwn", "text": f"Labels: {', '.join(inputs.labels)}"}
                    ]
                }
            ]
        }
        
        if inputs.context_data.get('pr_url'):
            message["blocks"].append({
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "View PR"},
                        "url": inputs.context_data['pr_url']
                    }
                ]
            })
        
        response = requests.post(webhook_url, json=message)
        
        return MultiPlatformOutputs(
            success=response.status_code == 200,
            platform_id="slack_message",
            error_message=None if response.status_code == 200 else "Failed to send Slack message"
        )
    except Exception as e:
        return MultiPlatformOutputs(success=False, error_message=str(e))

def send_discord_message(inputs: MultiPlatformInputs) -> MultiPlatformOutputs:
    """Send message to Discord."""
    try:
        webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
        
        # Create Discord embed
        embed = {
            "title": f"🤖 AutoPR: {inputs.title}",
            "description": inputs.description,
            "color": 0x00ff00,  # Green
            "fields": [
                {"name": "Priority", "value": inputs.priority, "inline": True},
                {"name": "Labels", "value": ", ".join(inputs.labels) or "None", "inline": True}
            ]
        }
        
        if inputs.context_data.get('pr_url'):
            embed["url"] = inputs.context_data['pr_url']
        
        message = {"embeds": [embed]}
        
        response = requests.post(webhook_url, json=message)
        
        return MultiPlatformOutputs(
            success=response.status_code == 204,  # Discord returns 204 for success
            platform_id="discord_message",
            error_message=None if response.status_code == 204 else "Failed to send Discord message"
        )
    except Exception as e:
        return MultiPlatformOutputs(success=False, error_message=str(e))

def create_notion_page(inputs: MultiPlatformInputs) -> MultiPlatformOutputs:
    """Create page in Notion."""
    try:
        headers = {
            "Authorization": f"Bearer {os.getenv('NOTION_API_KEY')}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        
        page_data = {
            "parent": {"database_id": os.getenv('NOTION_DATABASE_ID')},
            "properties": {
                "Title": {"title": [{"text": {"content": inputs.title}}]},
                "Priority": {"select": {"name": inputs.priority}},
                "Status": {"select": {"name": "Todo"}},
                "Labels": {"multi_select": [{"name": label} for label in inputs.labels]}
            },
            "children": [
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": inputs.description}}]
                    }
                }
            ]
        }
        
        response = requests.post(
            "https://api.notion.com/v1/pages",
            headers=headers,
            json=page_data
        )
        
        if response.status_code == 200:
            data = response.json()
            return MultiPlatformOutputs(
                success=True,
                platform_id=data["id"],
                platform_url=data["url"]
            )
    except Exception as e:
        return MultiPlatformOutputs(success=False, error_message=str(e))

def create_jira_ticket(inputs: MultiPlatformInputs) -> MultiPlatformOutputs:
    """Create ticket in Jira."""
    try:
        auth = (os.getenv('JIRA_EMAIL'), os.getenv('JIRA_API_TOKEN'))
        
        # Map priority
        priority_map = {
            "low": {"name": "Low"},
            "medium": {"name": "Medium"},
            "high": {"name": "High"},
            "critical": {"name": "Highest"}
        }
        
        issue_data = {
            "fields": {
                "project": {"key": os.getenv('JIRA_PROJECT_KEY')},
                "summary": inputs.title,
                "description": inputs.description,
                "issuetype": {"name": "Task"},
                "priority": priority_map.get(inputs.priority, {"name": "Medium"}),
                "labels": inputs.labels
            }
        }
        
        if inputs.assignee:
            issue_data["fields"]["assignee"] = {"name": inputs.assignee}
        
        response = requests.post(
            f"{os.getenv('JIRA_BASE_URL')}/rest/api/3/issue",
            auth=auth,
            json=issue_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            data = response.json()
            return MultiPlatformOutputs(
                success=True,
                platform_id=data["key"],
                platform_url=f"{os.getenv('JIRA_BASE_URL')}/browse/{data['key']}"
            )
    except Exception as e:
        return MultiPlatformOutputs(success=False, error_message=str(e)) 
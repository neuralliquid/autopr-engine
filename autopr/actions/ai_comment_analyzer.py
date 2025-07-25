"""
AutoPR Action: AI Comment Analyzer
Uses LLM to analyze PR comments and generate intelligent responses and fixes.
"""

import os
import json
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
import openai
from .base import Action


class AICommentAnalysisInputs(BaseModel):
    comment_body: str
    file_path: Optional[str] = None
    file_content: Optional[str] = None
    surrounding_context: Optional[str] = None
    pr_diff: Optional[str] = None


class AICommentAnalysisOutputs(BaseModel):
    intent: str  # "fix_request", "question", "suggestion", "praise", "complex_issue"
    confidence: float
    suggested_actions: List[str] = Field(default_factory=list)
    auto_fixable: bool
    fix_code: Optional[str] = None
    response_template: str
    issue_priority: str  # "low", "medium", "high", "critical"
    tags: List[str] = Field(default_factory=list)


def analyze_comment_with_ai(
    inputs: AICommentAnalysisInputs,
) -> AICommentAnalysisOutputs:
    """
    Uses LLM to analyze PR comment and determine best response strategy.
    """

    # Set up OpenAI client (or use local LLM)
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    system_prompt = """
    You are an expert code reviewer and automation assistant. Analyze PR comments to determine:
    1. The intent and sentiment of the comment
    2. Whether it can be automatically fixed
    3. What actions should be taken
    4. Priority level
    5. Appropriate tags
    
    Return JSON with analysis results.
    """

    user_prompt = f"""
    Analyze this PR comment:
    
    Comment: "{inputs.comment_body}"
    File: {inputs.file_path or "N/A"}
    
    Context:
    {inputs.file_content[:500] if inputs.file_content else "No file content available"}
    
    Determine:
    - Intent (fix_request, question, suggestion, praise, complex_issue)
    - Confidence (0.0-1.0)
    - Suggested actions
    - Whether it's auto-fixable
    - Fix code if applicable
    - Response template
    - Priority (low/medium/high/critical)
    - Relevant tags
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.1,
        )

        # Parse AI response
        content = response.choices[0].message.content
        if content is None:
            return fallback_analysis(inputs)
        ai_analysis = json.loads(content)

        return AICommentAnalysisOutputs(**ai_analysis)

    except Exception as e:
        # Fallback to rule-based analysis
        return fallback_analysis(inputs)


def fallback_analysis(inputs: AICommentAnalysisInputs) -> AICommentAnalysisOutputs:
    """Fallback rule-based analysis if AI fails."""
    comment_lower = inputs.comment_body.lower()

    # Simple rule-based classification
    if any(word in comment_lower for word in ["fix", "remove", "change", "update"]):
        intent = "fix_request"
        auto_fixable = True
    elif any(word in comment_lower for word in ["?", "how", "why", "what"]):
        intent = "question"
        auto_fixable = False
    else:
        intent = "suggestion"
        auto_fixable = False

    return AICommentAnalysisOutputs(
        intent=intent,
        confidence=0.6,
        suggested_actions=["create_issue"],
        auto_fixable=auto_fixable,
        response_template="Thanks for the feedback! I'll look into this.",
        issue_priority="medium",
        tags=["needs-review"],
    )


class AICommentAnalyzer(Action[AICommentAnalysisInputs, AICommentAnalysisOutputs]):
    """Action for analyzing PR comments with AI."""

    def __init__(self) -> None:
        super().__init__(
            name="ai_comment_analyzer",
            description="Uses LLM to analyze PR comments and generate intelligent responses and fixes",
            version="1.0.0",
        )

    async def execute(
        self, inputs: AICommentAnalysisInputs, context: Dict[str, Any]
    ) -> AICommentAnalysisOutputs:
        """Execute the AI comment analysis."""
        return analyze_comment_with_ai(inputs)

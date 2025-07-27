from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class PlatformDetectorInputs(BaseModel):
    repository_url: str
    commit_messages: List[str] = []
    workspace_path: str = "."
    package_json_content: Optional[str] = None
    git_log_depth: int = 50


class PlatformDetectorOutputs(BaseModel):
    primary_platform: str
    secondary_platforms: List[str] = Field(default_factory=list)
    confidence_scores: Dict[str, float] = Field(default_factory=dict)
    workflow_type: str  # "single_platform", "hybrid_workflow", "multi_platform"
    platform_specific_configs: Dict[str, Any] = Field(default_factory=dict)
    recommended_enhancements: List[str] = Field(default_factory=list)
    migration_opportunities: List[str] = Field(default_factory=list)
    hybrid_workflow_analysis: Optional[Dict[str, Any]] = None

"""
AutoPR Action Base Classes

Base classes and interfaces for action implementation.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, TypeVar, Generic
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

# Type variables for generic Action class
TInputs = TypeVar('TInputs')
TOutputs = TypeVar('TOutputs')


@dataclass
class ActionInputs:
    """
    Base class for action inputs.
    
    Actions should define their own input classes that inherit from this.
    """
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert inputs to dictionary."""
        return self.__dict__
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ActionInputs':
        """Create inputs from dictionary."""
        return cls(**data)


@dataclass
class ActionOutputs:
    """
    Base class for action outputs.
    
    Actions should define their own output classes that inherit from this.
    """
    
    success: bool = True
    message: str = ""
    data: Optional[Dict[str, Any]] = None
    
    def __post_init__(self) -> None:
        if self.data is None:
            self.data = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert outputs to dictionary."""
        return {
            "success": self.success,
            "message": self.message,
            "data": self.data
        }


class Action(ABC, Generic[TInputs, TOutputs]):
    """
    Base class for all AutoPR actions.
    
    Actions are discrete units of work that can be executed as part of workflows.
    Each action has a name, description, inputs, and outputs.
    """
    
    def __init__(self, name: str, description: str = "", version: str = "1.0.0"):
        """
        Initialize the action.
        
        Args:
            name: Unique action name
            description: Human-readable description
            version: Action version
        """
        self.name = name
        self.description = description
        self.version = version
        self.required_permissions: List[str] = []
        self.supported_platforms: List[str] = ["github"]
    
    @abstractmethod
    async def execute(self, inputs: TInputs, context: Dict[str, Any]) -> TOutputs:
        """
        Execute the action with given inputs.
        
        Args:
            inputs: Action inputs
            context: Execution context containing environment data
            
        Returns:
            Action execution result
        """
        pass
    
    async def validate_inputs(self, inputs: TInputs) -> None:
        """
        Validate action inputs.
        
        Args:
            inputs: Action inputs to validate
            
        Raises:
            ValidationError: If inputs are invalid
        """
        # Default implementation - can be overridden
        pass
    
    async def validate_outputs(self, outputs: TOutputs) -> None:
        """
        Validate action outputs.
        
        Args:
            outputs: Action outputs to validate
            
        Raises:
            ValidationError: If outputs are invalid
        """
        # Default implementation - can be overridden
        pass
    
    async def run(self, inputs: TInputs) -> TOutputs:
        """
        Run the action with given inputs (alternative method name for compatibility).
        
        Args:
            inputs: Action inputs
            
        Returns:
            Action execution result
        """
        # Default implementation calls execute with empty context
        return await self.execute(inputs, {})
    
    def get_input_schema(self) -> Dict[str, Any]:
        """
        Get JSON schema for action inputs.
        
        Returns:
            JSON schema dictionary
        """
        # Default implementation - can be overridden
        return {
            "type": "object",
            "properties": {},
            "required": []
        }
    
    def get_output_schema(self) -> Dict[str, Any]:
        """
        Get JSON schema for action outputs.
        
        Returns:
            JSON schema dictionary
        """
        # Default implementation
        return {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "message": {"type": "string"},
                "data": {"type": "object"}
            },
            "required": ["success"]
        }
    
    def supports_platform(self, platform: str) -> bool:
        """
        Check if this action supports the given platform.
        
        Args:
            platform: Platform name (e.g., 'github', 'gitlab')
            
        Returns:
            True if action supports this platform
        """
        return platform in self.supported_platforms
    
    def requires_permission(self, permission: str) -> bool:
        """
        Check if this action requires a specific permission.
        
        Args:
            permission: Permission name
            
        Returns:
            True if action requires this permission
        """
        return permission in self.required_permissions
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get action metadata.
        
        Returns:
            Dictionary containing action metadata
        """
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "required_permissions": self.required_permissions,
            "supported_platforms": self.supported_platforms,
            "input_schema": self.get_input_schema(),
            "output_schema": self.get_output_schema()
        }
    
    def __str__(self) -> str:
        return f"Action(name='{self.name}', version='{self.version}')"
    
    def __repr__(self) -> str:
        return self.__str__()


class GitHubAction(Action):
    """
    Base class for GitHub-specific actions.
    
    Provides common functionality for actions that interact with GitHub API.
    """
    
    def __init__(self, name: str, description: str = "", version: str = "1.0.0"):
        super().__init__(name, description, version)
        self.supported_platforms = ["github"]
        self.required_permissions.extend(["repo", "pull_requests"])
    
    def get_github_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract GitHub-specific context information.
        
        Args:
            context: Full execution context
            
        Returns:
            GitHub context dictionary
        """
        return {
            "repository": context.get("repository"),
            "pull_request": context.get("pull_request"),
            "issue": context.get("issue"),
            "sender": context.get("sender"),
            "installation": context.get("installation"),
            "github_token": context.get("github_token")
        }


class LLMAction(Action):
    """
    Base class for actions that use LLM providers.
    
    Provides common functionality for AI-powered actions.
    """
    
    def __init__(self, name: str, description: str = "", version: str = "1.0.0"):
        super().__init__(name, description, version)
        self.required_permissions.append("llm_access")
    
    def get_llm_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract LLM-specific context information.
        
        Args:
            context: Full execution context
            
        Returns:
            LLM context dictionary
        """
        return {
            "llm_provider": context.get("llm_provider"),
            "llm_config": context.get("llm_config"),
            "model_name": context.get("model_name"),
            "temperature": context.get("temperature", 0.7),
            "max_tokens": context.get("max_tokens", 2000)
        }

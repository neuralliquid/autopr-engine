"""
AutoPR Action Base Classes

Base classes and interfaces for action implementation.
"""

from autopr.actions.base import Action, ActionInputs, ActionOutputs, GitHubAction, LLMAction

__all__ = ["ActionInputs", "ActionOutputs", "Action", "GitHubAction", "LLMAction"]

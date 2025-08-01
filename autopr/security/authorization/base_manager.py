"""Base authorization manager definition."""

from abc import ABC, abstractmethod
from typing import Set

from .models import AuthorizationContext, Permission, ResourceType


class BaseAuthorizationManager(ABC):
    """Base class for authorization managers"""

    @abstractmethod
    def authorize(self, context: AuthorizationContext) -> bool:
        """Check if the given context is authorized"""
        pass

    @abstractmethod
    def grant_resource_permission(
        self,
        user_id: str,
        resource_type: ResourceType,
        resource_id: str,
        permissions: Set[Permission],
        granted_by: str,
    ) -> bool:
        """Grant permissions to a user for a specific resource"""
        pass

    @abstractmethod
    def revoke_resource_permission(
        self, user_id: str, resource_type: ResourceType, resource_id: str
    ) -> bool:
        """Revoke permissions from a user for a specific resource"""
        pass

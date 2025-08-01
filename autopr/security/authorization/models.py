"""Authorization models and data structures."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set

import pydantic


class Permission(Enum):
    """Available permissions for resources."""

    READ = "read"
    WRITE = "write"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    ADMIN = "admin"
    EXECUTE = "execute"
    MANAGE = "manage"


class ResourceType(Enum):
    """Types of resources that can be protected."""

    PROJECT = "project"
    REPOSITORY = "repository"
    WORKFLOW = "workflow"
    TEMPLATE = "template"
    USER = "user"
    ORGANIZATION = "organization"
    INTEGRATION = "integration"
    CONFIG = "config"


class AuthorizationContext(pydantic.BaseModel):
    """Context for authorization decisions."""

    user_id: str
    roles: List[str] = []
    permissions: List[Permission] = []
    resource_type: ResourceType
    resource_id: str
    action: Permission
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    explicit_permissions: Optional[Set[Permission]] = None
    user_role: Optional[str] = None
    additional_context: Optional[Dict[str, Any]] = None

    class Config:
        use_enum_values = True


class ResourcePermission(pydantic.BaseModel):
    """Permission granted to a user for a specific resource."""

    resource_type: ResourceType
    resource_id: str
    permissions: Set[Permission]
    granted_by: str
    granted_at: str = pydantic.Field(default_factory=lambda: datetime.utcnow().isoformat())

    class Config:
        use_enum_values = True


class PermissionPolicy(pydantic.BaseModel):
    """Permission policy definition."""

    name: str
    description: str = ""
    rules: List[Dict[str, Any]]
    created_at: str = pydantic.Field(default_factory=lambda: datetime.utcnow().isoformat())
    active: bool = True

    class Config:
        use_enum_values = True


class AuthorizationReport(pydantic.BaseModel):
    """Comprehensive authorization report."""

    generated_at: str = pydantic.Field(default_factory=lambda: datetime.utcnow().isoformat())
    summary: Dict[str, Any] = {}
    details: Dict[str, Any] = {}
    security_analysis: Dict[str, Any] = {}
    recommendations: List[str] = []

    class Config:
        use_enum_values = True

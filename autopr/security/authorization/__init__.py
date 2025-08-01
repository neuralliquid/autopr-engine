"""
Authorization module for AutoPR Engine.

This module provides comprehensive authorization and access control functionality
including role-based access control (RBAC), resource-based permissions, audit logging,
and caching for performance optimization.
"""

from .audit import AuthorizationAuditLogger
from .cache import PermissionCache
from .decorators import AuthorizationDecorator, require_permission
from .managers import (
    AuditedAuthorizationManager,
    BaseAuthorizationManager,
    CachedAuthorizationManager,
    EnterpriseAuthorizationManager,
)
from .middleware import AuthorizationMiddleware
from .models import AuthorizationContext, Permission, ResourcePermission, ResourceType
from .utils import (
    authorize_request,
    create_project_authorization_context,
    create_repository_authorization_context,
    create_template_authorization_context,
    create_workflow_authorization_context,
    get_access_logger,
    get_authorization_manager,
)

__all__ = [
    # Models
    "Permission",
    "ResourceType",
    "AuthorizationContext",
    "ResourcePermission",
    # Managers
    "BaseAuthorizationManager",
    "EnterpriseAuthorizationManager",
    "CachedAuthorizationManager",
    "AuditedAuthorizationManager",
    # Decorators
    "AuthorizationDecorator",
    "require_permission",
    # Middleware
    "AuthorizationMiddleware",
    # Cache
    "PermissionCache",
    # Audit
    "AuthorizationAuditLogger",
    # Utils
    "create_project_authorization_context",
    "create_repository_authorization_context",
    "create_workflow_authorization_context",
    "create_template_authorization_context",
    "authorize_request",
    "get_authorization_manager",
    "get_access_logger",
]

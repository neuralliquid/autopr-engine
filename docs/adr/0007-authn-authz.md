# 7. Authentication & Authorization

## Status
Proposed

## Context
AutoPR needs a robust security model to:
- Secure API endpoints
- Manage user identities
- Control access to resources
- Support multiple authentication providers
- Handle service-to-service auth

## Decision
We will implement a flexible authentication and authorization system with these components:

### Authentication
1. **JWT-based Authentication**
   - Short-lived access tokens (15-30 min)
   - Refresh tokens for session management
   - Stateless validation using public/private key pairs

2. **Supported Identity Providers**
   - GitHub OAuth (primary)
   - Email/Password (for local development)
   - Service Accounts (for CI/CD)
   - SSO (SAML/OIDC for enterprise)

3. **Token Structure**
   ```json
   {
     "sub": "user:123",
     "iss": "autopr",
     "exp": 1735689600,
     "iat": 1683158400,
     "scopes": ["repo:read", "repo:write"],
     "permissions": {
       "repositories": ["owner/repo1", "owner/repo2"]
     }
   }
   ```

### Authorization
1. **Role-Based Access Control (RBAC)**
   - Predefined roles (admin, maintainer, developer, reader)
   - Custom roles with granular permissions
   - Organization-level and repository-level permissions

2. **Attribute-Based Access Control (ABAC)**
   - Fine-grained permissions based on resource attributes
   - Time-based access controls
   - IP-based restrictions

3. **Policy as Code**
   - Rego (Open Policy Agent) for complex policies
   - GitOps-friendly policy definitions
   - Policy testing framework

### Implementation
```python
# Example FastAPI authentication middleware
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if not credentials:
            raise HTTPException(status_code=403, detail="Invalid authorization")

        if not self.verify_jwt(credentials.credentials):
            raise HTTPException(status_code=403, detail="Invalid token")

        return credentials.credentials

# Usage in FastAPI route
@app.get("/api/v1/repos/{owner}/{repo}")
async def get_repo(
    owner: str,
    repo: str,
    token: str = Depends(JWTBearer())
):
    # Token is valid, check authorization
    if not has_permission(token, "repo:read", owner=owner, repo=repo):
        raise HTTPException(status_code=403, detail="Not authorized")
    return {"status": "success"}
```

## Consequences
### Positive
- Strong security model
- Flexible authentication options
- Fine-grained access control
- Industry-standard practices
- Audit logging support

### Negative
- Increased complexity
- Token management overhead
- Learning curve for custom policies
- Performance impact

### Neutral
- Need for token rotation
- Session management
- Revocation handling

## Related Decisions
- [ADR-0004: API Versioning Strategy](0004-api-versioning-strategy.md)
- [ADR-0008: Audit Logging](0008-audit-logging.md)

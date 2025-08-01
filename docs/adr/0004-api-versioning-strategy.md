# 4. API Versioning Strategy

## Status

Proposed

## Context

As AutoPR evolves, we need a strategy for versioning our APIs to:

- Support backward compatibility
- Enable smooth upgrades
- Allow for breaking changes when necessary
- Provide clear migration paths

## Decision

We will implement the following versioning strategy:

### Versioning Scheme

- **Semantic Versioning (SemVer)**: `MAJOR.MINOR.PATCH`
  - **MAJOR**: Breaking changes
  - **MINOR**: Backward-compatible features
  - **PATCH**: Backward-compatible bug fixes

### Versioning Mechanisms

1. **URL Path Versioning**
   - Format: `/v{major}/api/...`
   - Example: `/v1/api/templates`

1. **Header Versioning**
   - Header: `Accept: application/vnd.autopr.v1+json`
   - For content negotiation

1. **Query Parameter** (for browser-based APIs)
   - Format: `?api-version=1.0`
   - Secondary fallback mechanism

### Deprecation Policy

- Announce deprecation in release notes
- Support deprecated versions for at least 6 months
- Provide migration guides
- Use `Deprecation` and `Sunset` HTTP headers

## Consequences

### Positive

- Clear upgrade paths
- Predictable lifecycle
- Better developer experience
- Smooth transitions

### Negative

- Additional complexity
- Need to maintain multiple versions
- Testing overhead

### Neutral

- Documentation requirements
- Monitoring needs

## Related Decisions

- [ADR-0002: gRPC for Cross-Language Communication](0002-grpc-communication.md)
- [ADR-0005: Configuration Management](0005-configuration-management.md)

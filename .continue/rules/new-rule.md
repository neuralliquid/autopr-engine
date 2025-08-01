# New Rule Template

## Rule Information

- **Rule ID**: `RULE-XXX`
- **Category**: [Security | Performance | Quality | Architecture | Testing | Documentation]
- **Priority**: [Critical | High | Medium | Low]
- **Created**: [YYYY-MM-DD]
- **Author**: [Name]
- **Status**: [Draft | Review | Active | Deprecated]

## Rule Description

Brief description of what this rule enforces and why it's important for enterprise development.

## Scope

- **Applies to**: [All Code | Specific Languages | Specific Components]
- **Models**: [GPT-4.1 | GPT-4o | Smart Router | All]
- **Commands**: [/architect | /security | /optimize | /test | /refactor | /explain | All]

## Rule Definition

### What This Rule Enforces

- Specific requirement 1
- Specific requirement 2
- Specific requirement 3

### What This Rule Prevents

- Anti-pattern 1
- Security vulnerability 2
- Performance issue 3

## Implementation

### System Message Addition

```
[Add this text to the system message for relevant models]
```

### Command Prompt Enhancement

```
[Add this text to specific command prompts]
```

### Validation Criteria

- [ ] Validation check 1
- [ ] Validation check 2
- [ ] Validation check 3

## Examples

### ✅ Good Example

```language
// Example of code that follows this rule
```

### ❌ Bad Example

```language
// Example of code that violates this rule
```

### 🔧 Corrected Example

```language
// Example showing how to fix the violation
```

## Testing the Rule

### Test Commands

```bash
# Test commands to verify rule compliance
```

### Expected Behavior

1. The AI should suggest...
2. The AI should flag...
3. The AI should include...

### Validation Script Addition

```bash
# Add this check to validate_agent_rules.sh
check_contains "Rule description" '.models[X].systemMessage' 'rule keyword'
```

## Integration Steps

### 1. Update Configuration

- [ ] Add to system message for relevant models
- [ ] Update command prompts if needed
- [ ] Add validation criteria

### 2. Update Validation Script

- [ ] Add compliance check
- [ ] Update test criteria
- [ ] Test validation logic

### 3. Documentation

- [ ] Update main rules document
- [ ] Add to command documentation
- [ ] Update team guidelines

### 4. Testing

- [ ] Test rule with sample code
- [ ] Verify AI follows rule
- [ ] Check validation passes
- [ ] Get team feedback

## Related Rules

- [Link to related rules]
- [Dependencies on other rules]
- [Conflicting rules to resolve]

## Changelog

- **[YYYY-MM-DD]**: Rule created
- **[YYYY-MM-DD]**: Rule updated (description of changes)
- **[YYYY-MM-DD]**: Rule activated

## Notes

Any additional notes, considerations, or future improvements for this rule.

#!/usr/bin/env python3
"""
Template Validators Module
=========================

Individual validation functions for template quality assurance.

Features:
- Modular validation functions by category
- Reusable validation components
- Extensible validation framework
- Detailed validation reporting
"""

import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set

from .validation_rules import ValidationRule, ValidationRuleSet


class ValidationSeverity(Enum):
    """Severity levels for validation issues."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationIssue:
    """Represents a validation issue found in a template."""

    severity: ValidationSeverity
    category: str
    message: str
    location: str
    suggestion: Optional[str] = None
    rule_id: str = ""


class StructureValidator:
    """Validates template structure and basic requirements."""

    @staticmethod
    def check_required_fields(
        data: Dict[str, Any], file_path: Path, rule: ValidationRule
    ) -> List[ValidationIssue]:
        """Check for required fields in template."""
        issues = []
        required_fields = rule.parameters.get("required_fields", []) if rule.parameters else []

        for field in required_fields:
            if field not in data:
                issues.append(
                    ValidationIssue(
                        ValidationSeverity.ERROR,
                        "structure",
                        f"Missing required field: {field}",
                        str(file_path),
                        f"Add '{field}' field to template root",
                        rule.rule_id,
                    )
                )

        return issues

    @staticmethod
    def check_field_types(
        data: Dict[str, Any], file_path: Path, rule: ValidationRule
    ) -> List[ValidationIssue]:
        """Validate field types are correct."""
        issues = []

        # Check name field
        if "name" in data and not isinstance(data["name"], str):
            issues.append(
                ValidationIssue(
                    ValidationSeverity.ERROR,
                    "structure",
                    "Field 'name' must be a string",
                    str(file_path),
                    "Change 'name' field to string type",
                    rule.rule_id,
                )
            )

        # Check description field
        if "description" in data and not isinstance(data["description"], str):
            issues.append(
                ValidationIssue(
                    ValidationSeverity.ERROR,
                    "structure",
                    "Field 'description' must be a string",
                    str(file_path),
                    "Change 'description' field to string type",
                    rule.rule_id,
                )
            )

        # Check platforms field
        if "platforms" in data and not isinstance(data["platforms"], list):
            issues.append(
                ValidationIssue(
                    ValidationSeverity.ERROR,
                    "structure",
                    "Field 'platforms' must be a list",
                    str(file_path),
                    "Change 'platforms' field to list type",
                    rule.rule_id,
                )
            )

        return issues

    @staticmethod
    def check_version_field(
        data: Dict[str, Any], file_path: Path, rule: ValidationRule
    ) -> List[ValidationIssue]:
        """Check for version field presence."""
        issues = []

        if "version" not in data:
            issues.append(
                ValidationIssue(
                    ValidationSeverity.WARNING,
                    "structure",
                    "Template should include a version field",
                    str(file_path),
                    "Add 'version' field with semantic version (e.g., '1.0.0')",
                    rule.rule_id,
                )
            )

        return issues


class MetadataValidator:
    """Validates template metadata quality."""

    @staticmethod
    def check_name_quality(
        data: Dict[str, Any], file_path: Path, rule: ValidationRule
    ) -> List[ValidationIssue]:
        """Check name field quality."""
        issues: List[ValidationIssue] = []

        if "name" not in data:
            return issues

        name = data["name"]
        min_length = rule.parameters.get("min_length", 3) if rule.parameters else 3
        max_length = rule.parameters.get("max_length", 100) if rule.parameters else 100

        if len(name) < min_length:
            issues.append(
                ValidationIssue(
                    ValidationSeverity.WARNING,
                    "metadata",
                    f"Template name is too short (minimum {min_length} characters)",
                    str(file_path),
                    "Use a more descriptive name",
                    rule.rule_id,
                )
            )

        if len(name) > max_length:
            issues.append(
                ValidationIssue(
                    ValidationSeverity.WARNING,
                    "metadata",
                    f"Template name is too long (maximum {max_length} characters)",
                    str(file_path),
                    "Use a more concise name",
                    rule.rule_id,
                )
            )

        return issues

    @staticmethod
    def check_description_quality(
        data: Dict[str, Any], file_path: Path, rule: ValidationRule
    ) -> List[ValidationIssue]:
        """Check description field quality."""
        issues: List[ValidationIssue] = []

        if "description" not in data:
            return issues

        description = data["description"]
        min_length = rule.parameters.get("min_length", 20) if rule.parameters else 20
        max_length = rule.parameters.get("max_length", 500) if rule.parameters else 500

        if len(description) < min_length:
            issues.append(
                ValidationIssue(
                    ValidationSeverity.ERROR,
                    "metadata",
                    f"Description is too short (minimum {min_length} characters)",
                    str(file_path),
                    "Provide a more detailed description",
                    rule.rule_id,
                )
            )

        if len(description) > max_length:
            issues.append(
                ValidationIssue(
                    ValidationSeverity.WARNING,
                    "metadata",
                    f"Description is too long (maximum {max_length} characters)",
                    str(file_path),
                    "Make description more concise",
                    rule.rule_id,
                )
            )

        return issues

    @staticmethod
    def check_category_validity(
        data: Dict[str, Any], file_path: Path, rule: ValidationRule
    ) -> List[ValidationIssue]:
        """Check category field validity."""
        issues: List[ValidationIssue] = []

        if "category" not in data:
            return issues

        category = data["category"]
        valid_categories = rule.parameters.get("valid_categories", []) if rule.parameters else []

        if valid_categories and category not in valid_categories:
            issues.append(
                ValidationIssue(
                    ValidationSeverity.WARNING,
                    "metadata",
                    f"Category '{category}' is not in valid categories: {', '.join(valid_categories)}",
                    str(file_path),
                    f"Use one of: {', '.join(valid_categories)}",
                    rule.rule_id,
                )
            )

        return issues


class VariablesValidator:
    """Validates template variables configuration."""

    @staticmethod
    def check_variable_descriptions(
        data: Dict[str, Any], file_path: Path, rule: ValidationRule
    ) -> List[ValidationIssue]:
        """Check that variables have descriptions."""
        issues: List[ValidationIssue] = []

        if "variables" not in data:
            return issues

        variables = data["variables"]
        if not isinstance(variables, dict):
            return issues

        for var_name, var_config in variables.items():
            if not isinstance(var_config, dict):
                continue

            if "description" not in var_config or not var_config["description"]:
                issues.append(
                    ValidationIssue(
                        ValidationSeverity.WARNING,
                        "variables",
                        f"Variable '{var_name}' missing description",
                        str(file_path),
                        f"Add description for variable '{var_name}'",
                        rule.rule_id,
                    )
                )

        return issues

    @staticmethod
    def check_variable_examples(
        data: Dict[str, Any], file_path: Path, rule: ValidationRule
    ) -> List[ValidationIssue]:
        """Check that variables have examples."""
        issues: List[ValidationIssue] = []

        if "variables" not in data:
            return issues

        variables = data["variables"]
        if not isinstance(variables, dict):
            return issues

        for var_name, var_config in variables.items():
            if not isinstance(var_config, dict):
                continue

            if "examples" not in var_config or not var_config["examples"]:
                issues.append(
                    ValidationIssue(
                        ValidationSeverity.WARNING,
                        "variables",
                        f"Variable '{var_name}' missing examples",
                        str(file_path),
                        f"Add examples for variable '{var_name}'",
                        rule.rule_id,
                    )
                )

        return issues

    @staticmethod
    def check_required_variables(
        data: Dict[str, Any], file_path: Path, rule: ValidationRule
    ) -> List[ValidationIssue]:
        """Check that required variables are properly marked."""
        issues: List[ValidationIssue] = []

        if "variables" not in data:
            return issues

        variables = data["variables"]
        if not isinstance(variables, dict):
            return issues

        for var_name, var_config in variables.items():
            if not isinstance(var_config, dict):
                continue

            # Check if variable seems required but not marked
            if (
                "required" not in var_config
                and var_config.get("type") in ["string", "number"]
                and "default" not in var_config
            ):
                issues.append(
                    ValidationIssue(
                        ValidationSeverity.WARNING,
                        "variables",
                        f"Variable '{var_name}' may need 'required' field",
                        str(file_path),
                        f"Add 'required: true/false' for variable '{var_name}'",
                        rule.rule_id,
                    )
                )

        return issues


class DocumentationValidator:
    """Validates documentation completeness."""

    @staticmethod
    def check_setup_instructions(
        data: Dict[str, Any], file_path: Path, rule: ValidationRule
    ) -> List[ValidationIssue]:
        """Check for setup instructions."""
        issues = []

        has_setup = (
            "setup_instructions" in data
            or "installation" in data
            or "getting_started" in data
            or (
                "documentation" in data
                and isinstance(data["documentation"], dict)
                and any(
                    key in data["documentation"]
                    for key in ["setup", "installation", "getting_started"]
                )
            )
        )

        if not has_setup:
            issues.append(
                ValidationIssue(
                    ValidationSeverity.WARNING,
                    "documentation",
                    "Template missing setup instructions",
                    str(file_path),
                    "Add setup_instructions, installation, or getting_started section",
                    rule.rule_id,
                )
            )

        return issues

    @staticmethod
    def check_best_practices(
        data: Dict[str, Any], file_path: Path, rule: ValidationRule
    ) -> List[ValidationIssue]:
        """Check for best practices documentation."""
        issues = []

        has_best_practices = "best_practices" in data or (
            "documentation" in data
            and isinstance(data["documentation"], dict)
            and "best_practices" in data["documentation"]
        )

        if not has_best_practices:
            issues.append(
                ValidationIssue(
                    ValidationSeverity.INFO,
                    "documentation",
                    "Template could benefit from best practices section",
                    str(file_path),
                    "Add best_practices section with recommendations",
                    rule.rule_id,
                )
            )

        return issues

    @staticmethod
    def check_troubleshooting(
        data: Dict[str, Any], file_path: Path, rule: ValidationRule
    ) -> List[ValidationIssue]:
        """Check for troubleshooting documentation."""
        issues = []

        has_troubleshooting = (
            "troubleshooting" in data
            or "faq" in data
            or (
                "documentation" in data
                and isinstance(data["documentation"], dict)
                and any(
                    key in data["documentation"]
                    for key in ["troubleshooting", "faq", "common_issues"]
                )
            )
        )

        if not has_troubleshooting:
            issues.append(
                ValidationIssue(
                    ValidationSeverity.INFO,
                    "documentation",
                    "Template could benefit from troubleshooting guide",
                    str(file_path),
                    "Add troubleshooting or faq section",
                    rule.rule_id,
                )
            )

        return issues


class ExamplesValidator:
    """Validates examples quality and completeness."""

    @staticmethod
    def check_example_presence(
        data: Dict[str, Any], file_path: Path, rule: ValidationRule
    ) -> List[ValidationIssue]:
        """Check for presence of examples."""
        issues = []

        if "examples" not in data or not data["examples"]:
            issues.append(
                ValidationIssue(
                    ValidationSeverity.WARNING,
                    "examples",
                    "Template missing examples",
                    str(file_path),
                    "Add examples section with practical use cases",
                    rule.rule_id,
                )
            )

        return issues

    @staticmethod
    def check_example_quality(
        data: Dict[str, Any], file_path: Path, rule: ValidationRule
    ) -> List[ValidationIssue]:
        """Check quality of examples."""
        issues: List[ValidationIssue] = []

        if "examples" not in data:
            return issues

        examples = data["examples"]
        if not isinstance(examples, dict):
            return issues

        for example_name, example_data in examples.items():
            if not isinstance(example_data, dict):
                continue

            # Check for description
            if "description" not in example_data:
                issues.append(
                    ValidationIssue(
                        ValidationSeverity.INFO,
                        "examples",
                        f"Example '{example_name}' missing description",
                        str(file_path),
                        f"Add description for example '{example_name}'",
                        rule.rule_id,
                    )
                )

            # Check for variables/configuration
            if "variables" not in example_data and "config" not in example_data:
                issues.append(
                    ValidationIssue(
                        ValidationSeverity.INFO,
                        "examples",
                        f"Example '{example_name}' missing configuration",
                        str(file_path),
                        f"Add variables or config for example '{example_name}'",
                        rule.rule_id,
                    )
                )

        return issues


class SecurityValidator:
    """Validates security considerations."""

    @staticmethod
    def check_hardcoded_secrets(
        data: Dict[str, Any], file_path: Path, rule: ValidationRule
    ) -> List[ValidationIssue]:
        """Check for hardcoded secrets or credentials."""
        issues = []

        # Convert data to string for pattern matching
        data_str = str(data).lower()

        # Common patterns for secrets
        secret_patterns = [
            r'password\s*[=:]\s*["\'][^"\']{3,}["\']',
            r'api_key\s*[=:]\s*["\'][^"\']{10,}["\']',
            r'secret\s*[=:]\s*["\'][^"\']{8,}["\']',
            r'token\s*[=:]\s*["\'][^"\']{10,}["\']',
            r'key\s*[=:]\s*["\'][^"\']{8,}["\']',
        ]

        for pattern in secret_patterns:
            if re.search(pattern, data_str):
                issues.append(
                    ValidationIssue(
                        ValidationSeverity.ERROR,
                        "security",
                        "Potential hardcoded secret or credential detected",
                        str(file_path),
                        "Use environment variables or configuration for secrets",
                        rule.rule_id,
                    )
                )
                break  # Only report once per template

        return issues

    @staticmethod
    def check_security_documentation(
        data: Dict[str, Any], file_path: Path, rule: ValidationRule
    ) -> List[ValidationIssue]:
        """Check for security documentation."""
        issues = []

        has_security_docs = (
            "security" in data
            or "security_considerations" in data
            or (
                "documentation" in data
                and isinstance(data["documentation"], dict)
                and any(
                    key in data["documentation"] for key in ["security", "security_considerations"]
                )
            )
        )

        if not has_security_docs:
            issues.append(
                ValidationIssue(
                    ValidationSeverity.WARNING,
                    "security",
                    "Template missing security documentation",
                    str(file_path),
                    "Add security or security_considerations section",
                    rule.rule_id,
                )
            )

        return issues


class PerformanceValidator:
    """Validates performance considerations."""

    @staticmethod
    def check_performance_documentation(
        data: Dict[str, Any], file_path: Path, rule: ValidationRule
    ) -> List[ValidationIssue]:
        """Check for performance documentation."""
        issues = []

        has_performance_docs = (
            "performance" in data
            or "performance_considerations" in data
            or (
                "documentation" in data
                and isinstance(data["documentation"], dict)
                and any(
                    key in data["documentation"]
                    for key in ["performance", "performance_considerations"]
                )
            )
        )

        if not has_performance_docs:
            issues.append(
                ValidationIssue(
                    ValidationSeverity.INFO,
                    "performance",
                    "Template could benefit from performance documentation",
                    str(file_path),
                    "Add performance or performance_considerations section",
                    rule.rule_id,
                )
            )

        return issues

    @staticmethod
    def check_resource_optimization(
        data: Dict[str, Any], file_path: Path, rule: ValidationRule
    ) -> List[ValidationIssue]:
        """Check for resource optimization considerations."""
        issues = []

        # Check for large embedded content
        data_str = str(data)
        if len(data_str) > 50000:  # 50KB threshold
            issues.append(
                ValidationIssue(
                    ValidationSeverity.WARNING,
                    "performance",
                    "Template file is quite large, consider optimization",
                    str(file_path),
                    "Consider splitting large content or using external references",
                    rule.rule_id,
                )
            )

        return issues


class ValidatorRegistry:
    """Registry of all validation functions."""

    def __init__(self) -> None:
        """Initialize the validator registry."""
        self._validators = {
            # Structure validators
            "check_required_fields": StructureValidator.check_required_fields,
            "check_field_types": StructureValidator.check_field_types,
            "check_version_field": StructureValidator.check_version_field,
            # Metadata validators
            "check_name_quality": MetadataValidator.check_name_quality,
            "check_description_quality": MetadataValidator.check_description_quality,
            "check_category_validity": MetadataValidator.check_category_validity,
            # Variables validators
            "check_variable_descriptions": VariablesValidator.check_variable_descriptions,
            "check_variable_examples": VariablesValidator.check_variable_examples,
            "check_required_variables": VariablesValidator.check_required_variables,
            # Documentation validators
            "check_setup_instructions": DocumentationValidator.check_setup_instructions,
            "check_best_practices": DocumentationValidator.check_best_practices,
            "check_troubleshooting": DocumentationValidator.check_troubleshooting,
            # Examples validators
            "check_example_presence": ExamplesValidator.check_example_presence,
            "check_example_quality": ExamplesValidator.check_example_quality,
            # Security validators
            "check_hardcoded_secrets": SecurityValidator.check_hardcoded_secrets,
            "check_security_documentation": SecurityValidator.check_security_documentation,
            # Performance validators
            "check_performance_documentation": PerformanceValidator.check_performance_documentation,
            "check_resource_optimization": PerformanceValidator.check_resource_optimization,
        }

    def get_validator(
        self, check_function: str
    ) -> Optional[Callable[[Dict[str, Any], Path, ValidationRule], List[ValidationIssue]]]:
        """Get a validator function by name."""
        return self._validators.get(check_function)

    def run_validation(
        self, check_function: str, data: Dict[str, Any], file_path: Path, rule: ValidationRule
    ) -> List[ValidationIssue]:
        """Run a specific validation check."""
        validator = self.get_validator(check_function)
        if validator is None:
            return [
                ValidationIssue(
                    ValidationSeverity.ERROR,
                    "system",
                    f"Unknown validation function: {check_function}",
                    str(file_path),
                    f"Check validation rule configuration for function '{check_function}'",
                    rule.rule_id,
                )
            ]

        try:
            return validator(data, file_path, rule)
        except Exception as e:
            return [
                ValidationIssue(
                    ValidationSeverity.ERROR,
                    "system",
                    f"Validation function '{check_function}' failed: {e}",
                    str(file_path),
                    f"Check validation function implementation for '{check_function}'",
                    rule.rule_id,
                )
            ]


# Global validator registry instance
_validator_registry = ValidatorRegistry()


def get_validator_registry() -> ValidatorRegistry:
    """Get the global validator registry instance."""
    return _validator_registry

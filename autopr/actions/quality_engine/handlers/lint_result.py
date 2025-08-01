from typing import TypedDict

from .lint_issue import LintIssue


class LintResult(TypedDict):
    issues: list[LintIssue]

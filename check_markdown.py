import os
import re
from pathlib import Path

# Configuration
MAX_LINE_LENGTH = 120
REQUIRE_BLANK_LINE_BEFORE_HEADING = True
REQUIRE_BLANK_LINE_AFTER_HEADING = True
ALLOW_MULTIPLE_BLANK_LINES = False

# Patterns
HEADING_PATTERN = re.compile(r"^#{1,6}\s+.+")
CODE_BLOCK_PATTERN = re.compile(r"^```")


class MarkdownLinter:
    def __init__(self, root_dir):
        self.root_dir = Path(root_dir)
        self.issues = []

    def check_file(self, file_path):
        """Check a single markdown file for linting issues."""
        relative_path = file_path.relative_to(self.root_dir)

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            in_code_block = False
            prev_line_was_heading = False
            prev_line_was_blank = False

            for i, line in enumerate(lines, 1):
                line = line.rstrip("\r\n")

                # Skip empty lines
                if not line.strip():
                    if prev_line_was_blank and not ALLOW_MULTIPLE_BLANK_LINES:
                        self.issues.append(
                            {
                                "file": str(relative_path),
                                "line": i,
                                "issue": "Multiple consecutive blank lines",
                                "code": "MD012",
                            }
                        )
                    prev_line_was_blank = True
                    continue

                # Check code blocks
                if CODE_BLOCK_PATTERN.match(line.strip()):
                    in_code_block = not in_code_block
                    continue

                if in_code_block:
                    continue

                # Check line length
                if len(line) > MAX_LINE_LENGTH:
                    self.issues.append(
                        {
                            "file": str(relative_path),
                            "line": i,
                            "issue": f"Line too long ({len(line)} > {MAX_LENGTH} characters)",
                            "code": "MD013",
                        }
                    )

                # Check headings
                if HEADING_PATTERN.match(line):
                    # Check for blank line before heading
                    if REQUIRE_BLANK_LINE_BEFORE_HEADING and i > 1 and lines[i - 2].strip() != "":
                        self.issues.append(
                            {
                                "file": str(relative_path),
                                "line": i,
                                "issue": "Missing blank line before heading",
                                "code": "MD022",
                            }
                        )

                    # Check for blank line after heading
                    if (
                        REQUIRE_BLANK_LINE_AFTER_HEADING
                        and i < len(lines)
                        and lines[i].strip() != ""
                    ):
                        self.issues.append(
                            {
                                "file": str(relative_path),
                                "line": i,
                                "issue": "Missing blank line after heading",
                                "code": "MD012",
                            }
                        )

                    prev_line_was_heading = True
                else:
                    prev_line_was_heading = False

                prev_line_was_blank = False

        except Exception as e:
            self.issues.append(
                {
                    "file": str(relative_path),
                    "line": 0,
                    "issue": f"Error reading file: {str(e)}",
                    "code": "ERROR",
                }
            )

    def check_directory(self):
        """Check all markdown files in the directory."""
        for root, _, files in os.walk(self.root_dir):
            for file in files:
                if file.lower().endswith(".md"):
                    file_path = Path(root) / file
                    self.check_file(file_path)

    def report_issues(self):
        """Print a report of all issues found."""
        if not self.issues:
            print("No markdown linting issues found!")
            return

        # Group issues by file
        issues_by_file = {}
        for issue in self.issues:
            if issue["file"] not in issues_by_file:
                issues_by_file[issue["file"]] = []
            issues_by_file[issue["file"]].append(issue)

        # Print report
        for file, file_issues in sorted(issues_by_file.items()):
            print(f"\n{file}:")
            for issue in sorted(file_issues, key=lambda x: x["line"]):
                print(f"  Line {issue['line']}: [{issue['code']}] {issue['issue']}")

        print(f"\nFound {len(self.issues)} issue(s) in {len(issues_by_file)} file(s)")
        return len(self.issues)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        root_dir = Path(sys.argv[1])
    else:
        root_dir = Path.cwd()

    linter = MarkdownLinter(root_dir)
    linter.check_directory()
    sys.exit(linter.report_issues() > 0)

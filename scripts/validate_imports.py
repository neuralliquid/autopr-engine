#!/usr/bin/env python3
"""
Import validation script for AutoPR Engine.

This script scans for broken imports and updates import paths after
documentation and code reorganization.
"""

import os
import re
import sys
from typing import Dict, List, Tuple


def find_python_files(directory: str) -> List[str]:
    """Find all Python files in the directory."""
    python_files = []
    for root, dirs, files in os.walk(directory):
        # Skip virtual environments and cache directories
        dirs[:] = [
            d for d in dirs if not d.startswith(".") and d not in ["__pycache__", ".venv", "venv"]
        ]

        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))

    return python_files


def extract_imports(file_path: str) -> List[Tuple[str, int, str]]:
    """Extract import statements from a Python file."""
    imports = []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        for line_num, line in enumerate(lines, 1):
            line = line.strip()

            # Match import statements
            import_patterns = [
                r"^import\s+([a-zA-Z_][a-zA-Z0-9_.]*)$",
                r"^from\s+([a-zA-Z_][a-zA-Z0-9_.]*)\s+import",
                r"^from\s+([a-zA-Z_][a-zA-Z0-9_.]*)\s+import\s+([a-zA-Z_][a-zA-Z0-9_,\s]*)",
            ]

            for pattern in import_patterns:
                match = re.match(pattern, line)
                if match:
                    module = match.group(1)
                    imports.append((module, line_num, line))
                    break

    except Exception as e:
        print(f"Error reading {file_path}: {e}")

    return imports


def check_import_validity(import_path: str, project_root: str) -> bool:
    """Check if an import path is valid."""
    if import_path.startswith("."):
        # Relative import - check if file exists
        return True  # Assume relative imports are valid for now

    # Check if it's a standard library module
    try:
        __import__(import_path)
        return True
    except ImportError:
        pass

    # Check if it's a local module
    parts = import_path.split(".")
    if parts[0] == "autopr":
        # Check if the autopr module exists
        module_path = os.path.join(project_root, *parts)
        if os.path.exists(module_path + ".py") or os.path.exists(
            os.path.join(module_path, "__init__.py")
        ):
            return True

    return False


def validate_imports(project_root: str) -> Dict[str, List[Tuple[str, int, str]]]:
    """Validate all imports in the project."""
    python_files = find_python_files(project_root)
    broken_imports = {}

    print(f"Scanning {len(python_files)} Python files...")

    for file_path in python_files:
        imports = extract_imports(file_path)
        file_broken_imports = []

        for module, line_num, line in imports:
            if not check_import_validity(module, project_root):
                file_broken_imports.append((module, line_num, line))

        if file_broken_imports:
            broken_imports[file_path] = file_broken_imports

    return broken_imports


def generate_import_report(broken_imports: Dict[str, List[Tuple[str, int, str]]]) -> str:
    """Generate a report of broken imports."""
    if not broken_imports:
        return "✅ No broken imports found!"

    report = ["❌ Broken Imports Found:", ""]

    for file_path, imports in broken_imports.items():
        report.append(f"📁 {file_path}:")
        for module, line_num, line in imports:
            report.append(f"  Line {line_num}: {line}")
        report.append("")

    return "\n".join(report)


def main():
    """Main function."""
    project_root = os.getcwd()

    print("🔍 AutoPR Engine Import Validation")
    print("=" * 50)

    # Validate imports
    broken_imports = validate_imports(project_root)

    # Generate report
    report = generate_import_report(broken_imports)
    print(report)

    # Save report to file
    report_file = os.path.join(project_root, "import_validation_report.txt")
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\n📄 Report saved to: {report_file}")

    if broken_imports:
        print(f"\n⚠️  Found {len(broken_imports)} files with broken imports")
        return 1
    else:
        print("\n✅ All imports are valid!")
        return 0


if __name__ == "__main__":
    sys.exit(main())

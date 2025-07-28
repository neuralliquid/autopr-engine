#!/usr/bin/env python3
"""
Code Quality Management Script for AutoPR Engine

This script provides convenient commands for running code quality tools
and managing the development workflow.
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List, Optional


def run_command(cmd: List[str], description: str, check: bool = True) -> bool:
    """Run a command and handle errors gracefully."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, check=check, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            if result.stdout.strip():
                print(result.stdout)
            return True
        else:
            print(f"❌ {description} failed")
            if result.stderr.strip():
                print(result.stderr)
            return False
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with error: {e}")
        if e.stderr:
            print(e.stderr)
        return False
    except FileNotFoundError:
        print(f"❌ Command not found. Make sure the tool is installed: {cmd[0]}")
        return False


def format_code() -> bool:
    """Format code using black and isort."""
    success = True

    # Run black
    success &= run_command(
        ["python", "-m", "black", ".", "--line-length", "100"], "Formatting code with Black"
    )

    # Run isort
    success &= run_command(
        ["python", "-m", "isort", ".", "--profile", "black"], "Sorting imports with isort"
    )

    return success


def lint_code() -> bool:
    """Run linting tools."""
    success = True

    # Run flake8
    success &= run_command(
        ["python", "-m", "flake8", ".", "--max-line-length", "100"],
        "Linting with flake8",
        check=False,
    )

    # Run mypy
    success &= run_command(
        ["python", "-m", "mypy", ".", "--config-file", "pyproject.toml"],
        "Type checking with mypy",
        check=False,
    )

    # Run bandit
    success &= run_command(
        ["python", "-m", "bandit", "-r", ".", "-c", "pyproject.toml"],
        "Security scanning with bandit",
        check=False,
    )

    return success


def run_tests() -> bool:
    """Run the test suite."""
    return run_command(
        ["python", "-m", "pytest", "-v", "--cov=autopr", "--cov-report=term-missing"],
        "Running test suite",
    )


def check_dependencies() -> bool:
    """Check for security vulnerabilities in dependencies."""
    return run_command(
        ["python", "-m", "safety", "check", "--json"],
        "Checking dependencies for security vulnerabilities",
        check=False,
    )


def install_pre_commit() -> bool:
    """Install pre-commit hooks."""
    success = True

    # Install pre-commit hooks
    success &= run_command(["python", "-m", "pre_commit", "install"], "Installing pre-commit hooks")

    # Install commit-msg hook for commitizen
    success &= run_command(
        ["python", "-m", "pre_commit", "install", "--hook-type", "commit-msg"],
        "Installing commit-msg hooks",
    )

    return success


def run_pre_commit(files: Optional[List[str]] = None) -> bool:
    """Run pre-commit hooks."""
    cmd = ["python", "-m", "pre_commit", "run"]

    if files:
        cmd.extend(["--files"] + files)
    else:
        cmd.append("--all-files")

    return run_command(cmd, "Running pre-commit hooks", check=False)


def full_check() -> bool:
    """Run all code quality checks."""
    print("🚀 Running full code quality check...\n")

    success = True

    # Format code
    success &= format_code()
    print()

    # Lint code
    success &= lint_code()
    print()

    # Run tests
    success &= run_tests()
    print()

    # Check dependencies
    success &= check_dependencies()
    print()

    if success:
        print("🎉 All code quality checks passed!")
    else:
        print("⚠️  Some code quality checks failed. Please review the output above.")

    return success


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Code Quality Management for AutoPR Engine")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Format command
    subparsers.add_parser("format", help="Format code with black and isort")

    # Lint command
    subparsers.add_parser("lint", help="Run linting tools (flake8, mypy, bandit)")

    # Test command
    subparsers.add_parser("test", help="Run test suite")

    # Security command
    subparsers.add_parser("security", help="Check dependencies for vulnerabilities")

    # Pre-commit commands
    pre_commit_parser = subparsers.add_parser("pre-commit", help="Pre-commit related commands")
    pre_commit_subparsers = pre_commit_parser.add_subparsers(dest="pre_commit_command")

    pre_commit_subparsers.add_parser("install", help="Install pre-commit hooks")

    run_parser = pre_commit_subparsers.add_parser("run", help="Run pre-commit hooks")
    run_parser.add_argument("files", nargs="*", help="Specific files to check")

    # Full check command
    subparsers.add_parser("check", help="Run all code quality checks")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Change to project root
    project_root = Path(__file__).parent.parent
    import os

    os.chdir(project_root)

    success = True

    if args.command == "format":
        success = format_code()
    elif args.command == "lint":
        success = lint_code()
    elif args.command == "test":
        success = run_tests()
    elif args.command == "security":
        success = check_dependencies()
    elif args.command == "pre-commit":
        if args.pre_commit_command == "install":
            success = install_pre_commit()
        elif args.pre_commit_command == "run":
            success = run_pre_commit(args.files if args.files else None)
        else:
            pre_commit_parser.print_help()
            return 1
    elif args.command == "check":
        success = full_check()

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

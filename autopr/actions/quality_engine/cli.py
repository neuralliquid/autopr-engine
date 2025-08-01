"""
Command-line interface for the quality engine
"""

import argparse
import asyncio
import glob
import json
from typing import List

from .di import get_engine
from .models import QualityInputs, QualityMode


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments for the quality engine.

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(description="AutoPR Quality Engine")
    parser.add_argument(
        "--mode",
        choices=["fast", "comprehensive", "ai_enhanced", "smart"],
        default="smart",
        help="Quality check mode",
    )
    parser.add_argument("--files", nargs="*", help="Files to check (supports glob patterns)")
    parser.add_argument("--config", default="pyproject.toml", help="Path to configuration file")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--ai-provider", help="AI provider to use for AI-enhanced mode")
    parser.add_argument("--ai-model", help="AI model to use for AI-enhanced mode")

    return parser.parse_args()


def resolve_file_patterns(patterns: List[str]) -> List[str]:
    """Resolve glob patterns to actual file paths.

    Args:
        patterns: List of file patterns

    Returns:
        List of resolved file paths
    """
    all_files = []
    for pattern in patterns:
        matched_files = glob.glob(pattern, recursive=True)
        all_files.extend(matched_files)
    return all_files


async def main() -> None:
    """Main entry point for the CLI."""
    args = parse_arguments()

    # Handle file globs
    all_files = []
    if args.files:
        all_files = resolve_file_patterns(args.files)

    inputs = QualityInputs(
        mode=QualityMode(args.mode),
        files=all_files,
        config_path=args.config,
        verbose=args.verbose,
        ai_provider=args.ai_provider,
        ai_model=args.ai_model,
    )

    # Get the pre-configured engine from the DI container
    engine = get_engine()

    result = await engine.run(inputs)
    print(json.dumps(result.model_dump(), indent=2))


if __name__ == "__main__":
    asyncio.run(main())

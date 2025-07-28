import os
from pathlib import Path


def find_markdown_files(root_dir):
    """Find all markdown files in the given directory and its subdirectories."""
    root_path = Path(root_dir)
    markdown_files = []

    for root, _, files in os.walk(root_path):
        for file in files:
            if file.lower().endswith((".md", ".markdown")):
                file_path = Path(root) / file
                markdown_files.append(file_path.relative_to(root_path))

    return sorted(markdown_files)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        root_dir = sys.argv[1]
    else:
        root_dir = os.getcwd()

    print(f"Searching for markdown files in: {root_dir}")
    files = find_markdown_files(root_dir)

    if not files:
        print("No markdown files found!")
    else:
        print("\nFound markdown files:")
        for file in files:
            print(f"- {file}")
        print(f"\nTotal: {len(files)} markdown files found")

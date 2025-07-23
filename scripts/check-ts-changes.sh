#!/bin/bash

# Get list of staged and unstaged TS/TSX files
CHANGED_TS_FILES=$(git diff --name-only --diff-filter=ACMR | grep -E \"\\.tsx?$\" || true)
STAGED_TS_FILES=$(git diff --cached --name-only --diff-filter=ACMR | grep -E \"\\.tsx?$\" || true)

# Combine the lists and remove duplicates
ALL_CHANGED_FILES=$(echo "$CHANGED_TS_FILES"$"\\n""$STAGED_TS_FILES" | sort | uniq)

# If there are no changed TypeScript files, exit successfully
if [ -z "$ALL_CHANGED_FILES" ]; then
  echo "No TypeScript files have been changed."
  exit 0
fi

# Create a temporary tsconfig that includes only the changed files
TMP_TSCONFIG="tsconfig.check.json"
[ -f "$TMP_TSCONFIG" ] && rm "$TMP_TSCONFIG"
trap 'rm -f "$TMP_TSCONFIG"' EXIT

cat > $TMP_TSCONFIG << JSON
{
  "extends": "./tsconfig.json",
  "include": [
$(echo "$ALL_CHANGED_FILES" | sed "s/^/    \\"/;s/$/\\"/" | paste -sd "," -)
  ]
}
JSON

# Run TypeScript check on only the changed files
echo "Checking TypeScript types for changed files..."

if ! ./node_modules/.bin/tsc --project $TMP_TSCONFIG --noEmit; then
  echo "TypeScript check completed with issues"
  exit 1
fi

echo "TypeScript check completed."
exit 0

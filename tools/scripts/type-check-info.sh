#!/bin/bash

echo "Running TypeScript type check (informational only)..."
./node_modules/.bin/tsc --noEmit || true

echo "TypeScript check completed. Any errors shown above are for information only."
echo "The above type checking is provided for information only and will not block your work."
exit 0

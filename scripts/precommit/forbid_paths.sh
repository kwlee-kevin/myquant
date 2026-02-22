#!/usr/bin/env bash
set -euo pipefail

blocked_regex='(^|/)(\.env$|\.DS_Store$|\.venv/|venv/|node_modules/|frontend/node_modules/|frontend/\.next/|\.next/)'

files=$(git diff --cached --name-only)
if [[ -z "$files" ]]; then
  exit 0
fi

violations=()
while IFS= read -r file; do
  [[ -z "$file" ]] && continue
  if [[ "$file" =~ $blocked_regex ]]; then
    violations+=("$file")
  fi
done <<< "$files"

if (( ${#violations[@]} > 0 )); then
  echo "Blocked files detected. Remove these from commit:" >&2
  for file in "${violations[@]}"; do
    echo "  - $file" >&2
  done
  exit 1
fi

exit 0

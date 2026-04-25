#!/usr/bin/env bash
# Reads all non-git files in this directory tree and prints their contents.

ROOT="$(cd "$(dirname "$0")" && pwd)"
SUCCESS=0
FAIL=0

while IFS= read -r -d '' file; do
  echo "==== $file ===="
  if cat "$file"; then
    echo ""
    ((SUCCESS++))
  else
    echo "[ERROR: could not read $file]"
    ((FAIL++))
  fi
done < <(find "$ROOT" -not -path '*/.git/*' -type f -not -name "$(basename "$0")" -print0 | sort -z)

echo ""
echo "Done. Read: $SUCCESS file(s), Errors: $FAIL"

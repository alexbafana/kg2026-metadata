#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 path/to/file.ttl" >&2
  exit 64
fi

if command -v riot >/dev/null 2>&1; then
  riot --validate "$1"
elif command -v riotcmd >/dev/null 2>&1; then
  riotcmd --validate "$1"
else
  echo "Apache Jena RIOT was not found. Install Jena and rerun; no validation result was produced." >&2
  exit 127
fi

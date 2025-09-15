#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

export DOCKER_CONFIG="${HOME}/.config/podman/docker-empty"
mkdir -p "$DOCKER_CONFIG"

echo "==> Starting Podman VM (if needed)"
podman machine start >/dev/null 2>&1 || true

echo "==> Bringing up web + db"
exec podman-compose up --build

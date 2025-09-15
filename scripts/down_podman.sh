#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

export DOCKER_CONFIG="${HOME}/.config/podman/docker-empty"
exec podman-compose down

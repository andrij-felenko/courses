#!/usr/bin/env bash
set -euo pipefail

DISTROS=("debian:10" "debian:11" "ubuntu:20.04" "ubuntu:22.04" "almalinux:8" "alpine:latest")

for DISTRO in "${DISTROS[@]}"; do
    echo "[*] Тестування бандла у середовищі $DISTRO..."
    docker run --rm -v "$(pwd)/dist:/app" "$DISTRO" /app/app.sh --version
    echo "[✓] Успішно пройдено для $DISTRO"
done

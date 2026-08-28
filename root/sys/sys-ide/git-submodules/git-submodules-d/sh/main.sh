#!/usr/bin/env bash
set -euo pipefail

UPSTREAM_TAG="v2.2.0"
TARGET_DIR="third_party/lwip"

rm -rf "${TARGET_DIR}"
git clone --depth 1 --branch "${UPSTREAM_TAG}" https://github.com/lwip-tcpip/lwip.git "${TARGET_DIR}"
rm -rf "${TARGET_DIR}/.git"

# Накладання обов'язкових локальних патчів
git apply --directory="${TARGET_DIR}" patches/0001-lwip-custom-pbuf-pool.patch

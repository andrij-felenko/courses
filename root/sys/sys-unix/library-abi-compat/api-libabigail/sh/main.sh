#!/usr/bin/env bash
set -euo pipefail

# 1. Збирання поточного коду з прапорцями DWARF
gcc -g -O2 -shared -fPIC -Wl,-soname,libtarget.so.1 -o build_new/libtarget.so src/*.c

# 2. Витягування еталонного зліпку ABI з репозиторію
ABIDIFF_SUPPR="config/abi-suppressions.suppr"
REFERENCE_ABI="config/reference-abi-1.0.xml"

# 3. Виконання перевірки abidiff
if ! abidiff --suppressions "${ABIDIFF_SUPPR}" "${REFERENCE_ABI}" build_new/libtarget.so; then
    echo "ERROR: ABI break detected! Please review structural changes or update SONAME version."
    exit 1
fi

echo "SUCCESS: ABI compatibility confirmed."

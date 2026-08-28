#!/usr/bin/env bash
# Розшифрувати адреси з логу поля. Ключ — Build-ID або версія.
#   decode.sh 4e9f2a1c...   0x400f360d 0x400dbf56     ← за Build-ID (надійно)
#   decode.sh v:2.4.1       0x400f360d 0x400dbf56     ← за версією (через місток)
set -euo pipefail

STORE="/srv/symbols"
ADDR2LINE="xtensa-esp32-elf-addr2line"
KEY="$1"; shift          # ключ; решта аргументів — адреси з рядка Backtrace:

# Якщо ключ заданий як версія (v:2.4.1) — спершу перейти через місток до Build-ID.
if [[ "$KEY" == v:* ]]; then
    VERSION="${KEY#v:}"
    MAP="$STORE/by-version/$VERSION.txt"
    [ -f "$MAP" ] || { echo "Немає запису для версії $VERSION" >&2; exit 1; }
    BUILD_ID=$(cat "$MAP")
else
    BUILD_ID="$KEY"
fi

# За Build-ID — пряма адреса файлу, без пошуку.
ELF="$STORE/.build-id/${BUILD_ID:0:2}/${BUILD_ID:2}.elf"
[ -f "$ELF" ] || { echo "Немає символів для Build-ID $BUILD_ID" >&2; exit 1; }

# Той самий робочий набір прапорців addr2line з теми: -pfiaC.
"$ADDR2LINE" -pfiaC -e "$ELF" "$@"

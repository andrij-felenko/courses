#!/usr/bin/env bash
# scripts/overlay.sh [link|copy|auto] — покласти custom/ усередину дерева апстриму
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$ROOT/upstream/qgroundcontrol"
DST="$SRC/custom"
MODE="${1:-${QGC_OVERLAY_MODE:-auto}}"

if [ ! -f "$SRC/CMakeLists.txt" ]; then
    echo "Підмодуль не витягнуто: git submodule update --init --recursive" >&2
    exit 1
fi

# 1. Хай git усередині підмодуля не рахує нашу теку за сміття в дереві.
#    У підмодуля .git — файл-указівник, тому справжній каталог питаємо в git.
GITDIR="$(git -C "$SRC" rev-parse --absolute-git-dir)"
mkdir -p "$GITDIR/info"
grep -qxF '/custom/' "$GITDIR/info/exclude" 2>/dev/null \
    || echo '/custom/' >> "$GITDIR/info/exclude"

# 2. Прибрати попереднє накладання, яким би воно не було.
#    Перевірка на посилання мусить іти першою: для посилання на теку -d теж істинне.
if [ -L "$DST" ]; then
    rm -f "$DST"
elif [ -d "$DST" ]; then
    rm -rf "$DST"
fi

# 3. Покласти нове.
if [ "$MODE" = auto ]; then
    if [ -n "${CI:-}" ]; then MODE=copy; else MODE=link; fi
fi

case "$MODE" in
    link) ln -s ../../custom "$DST" ;;
    copy) cmake -E copy_directory "$ROOT/custom" "$DST" ;;
    *)    echo "Невідомий режим: $MODE (link|copy|auto)" >&2; exit 2 ;;
esac

echo "Накладку покладено ($MODE): $DST"

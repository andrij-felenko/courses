#!/usr/bin/env bash
# scripts/bump-upstream.sh v5.0.8 — перевести підмодуль на тег і показати, що змінилося
set -euo pipefail

TAG="${1:?вкажіть тег апстриму, напр. v5.0.8}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$ROOT/upstream/qgroundcontrol"

OLD="$(git -C "$SRC" rev-parse HEAD)"

git -C "$SRC" fetch --tags --force origin
git -C "$SRC" checkout --detach "refs/tags/$TAG"
git -C "$SRC" submodule update --init --recursive

NEW="$(git -C "$SRC" rev-parse HEAD)"
if [ "$OLD" = "$NEW" ]; then echo "Уже на $TAG"; exit 0; fi

echo "== Що змінилося в точках, за які ми чіпляємось =="
# Розбиття на слова тут навмисне: у переліку шляхів пробілів немає.
WATCH="$(grep -vE '^[[:space:]]*(#|$)' "$ROOT/upstream-watch.txt" | tr '\n' ' ')"
git -C "$SRC" diff --stat "$OLD..$NEW" -- $WATCH

echo
echo "== Свіжий знімок чинних ручок збірки =="
rm -rf "$ROOT/build"                       # кеш переживає зникнення змінних — а нам треба, щоб не переживав
cmake -S "$SRC" -B "$ROOT/build" -DQGC_CUSTOM_DIR=custom -DCMAKE_BUILD_TYPE=Release >/dev/null
cmake -N -LA "$ROOT/build" | grep '^QGC_' \
    | sed "s#$ROOT#@ROOT@#g" | sort > "$ROOT/options.now"
diff "$ROOT/options.snapshot" "$ROOT/options.now" || true

git -C "$ROOT" add upstream/qgroundcontrol
echo
echo "Вказівник переставлено й підготовлено до коміту. Перегляньте різницю знімка вище,"
echo "оновіть options.snapshot свідомо — і лише тоді комітьте."

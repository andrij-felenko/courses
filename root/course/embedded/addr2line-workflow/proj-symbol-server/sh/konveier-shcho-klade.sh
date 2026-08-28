#!/usr/bin/env bash
# Викликається в кінці кожної релізної збірки. Кладе .elf у сховище символів
# під його Build-ID і реєструє відповідність версія → Build-ID. Жодної ручної праці.
set -euo pipefail

ELF="build/firmware.elf"          # свіжозібраний образ із повним DWARF
VERSION="$1"                       # версія цієї збірки, напр. 2.4.1
STORE="/srv/symbols"               # корінь сховища символів
READELF="xtensa-esp32-elf-readelf"

# 1. Дістати Build-ID із .elf — той самий 40-значний хеш, що його надрукує прошивка.
BUILD_ID=$("$READELF" -n "$ELF" \
    | awk '/Build ID:/ { print $3 }')

if [ -z "$BUILD_ID" ]; then
    echo "ПОМИЛКА: у $ELF немає Build-ID. Чи ввімкнено -Wl,--build-id?" >&2
    exit 1
fi

# 2. Розкласти за схемою .build-id/<перші 2>/<решта>.elf і покласти ОРИГІНАЛ.
SUBDIR="${BUILD_ID:0:2}"
FNAME="${BUILD_ID:2}.elf"
DEST="$STORE/.build-id/$SUBDIR"
mkdir -p "$DEST"
cp "$ELF" "$DEST/$FNAME"

# 3. Зареєструвати місток версія → Build-ID, щоб лог із самою версією теж знайшов словник.
mkdir -p "$STORE/by-version"
echo "$BUILD_ID" > "$STORE/by-version/$VERSION.txt"

echo "Збережено: версія $VERSION  Build-ID $BUILD_ID"
echo "  → $DEST/$FNAME"

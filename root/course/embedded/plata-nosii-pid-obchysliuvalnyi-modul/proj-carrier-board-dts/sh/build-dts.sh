#!/usr/bin/env bash
# build-dts.sh — препроцесування, компіляція та встановлення дерева пристроїв
# плати-носія. Виклик: ./build-dts.sh [install]
set -euo pipefail

KDIR=${KDIR:-/usr/src/linux}
ARCH_DTS="$KDIR/arch/arm64/boot/dts"
SRC_DIR="$(cd "$(dirname "$0")/../dts" && pwd)"
OUT_DIR="$(pwd)/build"
BOOT_DIR=${BOOT_DIR:-/boot/firmware}

die() { echo "build-dts: $*" >&2; exit 1; }

command -v dtc >/dev/null || die "нема dtc — поставте пакет device-tree-compiler"
command -v cpp >/dev/null || die "нема cpp — потрібен C-препроцесор"
[ -d "$ARCH_DTS/broadcom" ] || die "не бачу дерева ядра в $KDIR (задайте KDIR=)"

# Прапорець -@ з'явився в dtc 1.4.4; без нього не буде вузла __symbols__.
dtc_version=$(dtc --version | awk '{print $NF; exit}')
echo "dtc $dtc_version, дерево ядра $KDIR"

mkdir -p "$OUT_DIR"

# .dts не є чистим DTS: у ньому #include та макроси з dt-bindings,
# тому спершу через препроцесор, і лише потім у dtc.
preprocess() {
	local src=$1 dst=$2
	cpp -nostdinc -undef -D__DTS__ -x assembler-with-cpp \
		-I "$KDIR/include" \
		-I "$ARCH_DTS" \
		-I "$ARCH_DTS/broadcom" \
		-I "$SRC_DIR" \
		-o "$dst" "$src"
}

echo "==> carrier-board.dts"
preprocess "$SRC_DIR/carrier-board.dts" "$OUT_DIR/carrier-board.pre.dts"
dtc -@ -q -I dts -O dtb \
	-o "$OUT_DIR/carrier-board.dtb" "$OUT_DIR/carrier-board.pre.dts"

echo "==> sensor-hat.dtso"
preprocess "$SRC_DIR/overlays/sensor-hat.dtso" "$OUT_DIR/sensor-hat.pre.dts"
dtc -@ -q -I dts -O dtb \
	-o "$OUT_DIR/sensor-hat.dtbo" "$OUT_DIR/sensor-hat.pre.dts"

# Перевірка, що таблиця символів справді на місці: без неї цілі оверлею
# нема на що відобразити, і злиття мовчки не спрацює вже під час завантаження.
fdtget "$OUT_DIR/carrier-board.dtb" /__symbols__ i2c1 >/dev/null 2>&1 \
	|| die "у базовому блобі нема __symbols__ — забули -@"

# Пробне злиття на хості: те саме, що зробить U-Boot чи ядро, але тут
# помилка видна одразу, а не мертвою шиною на платі.
cp "$OUT_DIR/carrier-board.dtb" "$OUT_DIR/merged.dtb"
fdtoverlay -i "$OUT_DIR/carrier-board.dtb" -o "$OUT_DIR/merged.dtb" \
	"$OUT_DIR/sensor-hat.dtbo" || die "оверлей не лягає на базове дерево"

ls -l "$OUT_DIR"/*.dtb "$OUT_DIR"/*.dtbo

if [ "${1:-}" = "install" ]; then
	[ "$(id -u)" -eq 0 ] || die "встановлення в $BOOT_DIR потребує root"
	install -m 0644 "$OUT_DIR/carrier-board.dtb" "$BOOT_DIR/carrier-board.dtb"
	install -d "$BOOT_DIR/overlays"
	install -m 0644 "$OUT_DIR/sensor-hat.dtbo" "$BOOT_DIR/overlays/sensor-hat.dtbo"
	sync
	echo "встановлено; допишіть у config.txt device_tree=carrier-board.dtb"
fi

#!/usr/bin/env bash
# inspect-devicetree.sh — що з описаного заліза ядро справді побачило.
set -uo pipefail

DT=/proc/device-tree
I2C_BUS=${I2C_BUS:-1}

[ -d "$DT" ] || { echo "нема $DT: ядро зібране без CONFIG_PROC_FS або OF" >&2; exit 1; }

# Властивості дерева — рядки з нульовим байтом на кінці, а список
# compatible це кілька таких рядків підряд. Тому tr, а не cat.
prop() {
	[ -f "$1" ] && tr '\0' '\n' <"$1" | paste -sd' ' -
}

echo "== Плата =="
echo "model:      $(prop "$DT/model")"
echo "compatible: $(prop "$DT/compatible")"

echo
echo "== Вузли на шинах =="
for node in "$DT"/soc/i2c@*/*/ "$DT"/soc/spi@*/*/; do
	[ -d "$node" ] || continue
	compat=$(prop "$node/compatible")
	[ -n "$compat" ] || continue
	printf '%-46s %s\n' "${node#"$DT"}" "$compat"
done

echo
echo "== Прив'язка драйверів (порожнє = probe не відбувся) =="
for dev in /sys/bus/i2c/devices/"$I2C_BUS"-00*; do
	[ -e "$dev" ] || continue
	drv=$(basename "$(readlink -f "$dev/driver" 2>/dev/null)" 2>/dev/null)
	printf '%-16s %-14s %s\n' "$(basename "$dev")" "$(cat "$dev/name" 2>/dev/null)" \
		"${drv:-БЕЗ ДРАЙВЕРА}"
done

echo
echo "== Підсистеми =="
for h in /sys/class/hwmon/hwmon*; do
	[ -e "$h/name" ] || continue
	echo "hwmon: $(cat "$h/name") -> $h"
done
for r in /sys/class/rtc/rtc*; do
	[ -e "$r/name" ] || continue
	echo "rtc:   $(cat "$r/name") -> /dev/$(basename "$r")"
done
ip -brief link show can0 2>/dev/null || echo "can0: інтерфейс не зареєстровано"

echo
echo "== Мультиплексор виводів =="
grep -E 'pin (2|3|8|9|16|17|22|24|25|26) ' \
	/sys/kernel/debug/pinctrl/*gpio/pinmux-pins 2>/dev/null \
	|| echo "debugfs недоступний (потрібен root і CONFIG_DEBUG_FS)"

echo
echo "== Зворотне декомпілювання активного дерева =="
if command -v dtc >/dev/null; then
	dtc -I fs -O dts -q "$DT" >current-running-tree.dts
	echo "записано current-running-tree.dts ($(wc -l <current-running-tree.dts) рядків)"
else
	echo "dtc не встановлено — пропущено"
fi

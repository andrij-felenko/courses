#!/bin/sh
# /init — перший процес системи (PID 1) усередині initramfs, фаза 4.
#
# Задача рівно одна: підняти стільки простору користувача, щоб зібрати
# справжнє сховище й змонтувати його в /sysroot. Виконуваний код і всі
# утиліти тут лежать у пам'яті (rootfs), диска система ще не бачить.
#
# Будь-який вихід звідси, крім останнього рядка, означає паніку ядра:
# PID 1 завершуватися не має права.

set -u

PATH=/sbin:/bin:/usr/sbin:/usr/bin
export PATH

log() {
	# Поки консоль не відкрита як слід, повідомлення йде в буфер ядра.
	echo "init: $*" >/dev/kmsg 2>/dev/null || echo "init: $*"
}

panic() {
	log "ПАНІКА: $*"
	log "падаю в аварійну оболонку — вихід із неї вб'є PID 1"
	exec sh -i
}

# --- 1. Віртуальні файлові системи ------------------------------------------
# Без /proc немає /proc/cmdline, без /sys — жодної інформації про залізо,
# без devtmpfs у /dev не з'являться вузли дисків.
mount_pseudo() {
	mkdir -p /proc /sys /dev /run /sysroot
	mount -t proc -o nosuid,noexec,nodev proc /proc ||
		panic "не змонтувався /proc"
	mount -t sysfs -o nosuid,noexec,nodev sys /sys ||
		panic "не змонтувався /sys"
	mount -t devtmpfs -o nosuid,mode=0755 dev /dev ||
		panic "не змонтувався /dev"
	mount -t tmpfs -o nosuid,nodev,mode=0755 run /run ||
		panic "не змонтувався /run"
}

# --- 2. Параметри ядра ------------------------------------------------------
# Усе, що знає про корінь, завантажувач поклав у cmdline (фаза 2).
root_spec=""
root_fstype="auto"
root_flags=""
root_mode="ro"
luks_uuids=""
user_init="/sbin/init"

parse_cmdline() {
	for arg in $(cat /proc/cmdline); do
		case "$arg" in
		root=*)         root_spec=${arg#root=} ;;
		rootfstype=*)   root_fstype=${arg#rootfstype=} ;;
		rootflags=*)    root_flags=${arg#rootflags=} ;;
		ro)             root_mode="ro" ;;
		rw)             root_mode="rw" ;;
		rd.luks.uuid=*) luks_uuids="$luks_uuids ${arg#rd.luks.uuid=}" ;;
		init=*)         user_init=${arg#init=} ;;
		esac
	done
	[ -n "$root_spec" ] || panic "у cmdline немає root="
}

# root= задають не лише шляхом: мітка переживає перенумерацію дисків,
# а UUID — ще й переставляння в інший порт.
resolve_spec() {
	case "$1" in
	UUID=*)     echo "/dev/disk/by-uuid/${1#UUID=}" ;;
	PARTUUID=*) echo "/dev/disk/by-partuuid/${1#PARTUUID=}" ;;
	LABEL=*)    echo "/dev/disk/by-label/${1#LABEL=}" ;;
	*)          echo "$1" ;;
	esac
}

# Пристрій з'являється не миттєво: udev іще розбирає події від ядра.
wait_for_device() {
	dev=$1
	waited=0
	while [ ! -b "$dev" ]; do
		[ "$waited" -ge 30 ] && return 1
		udevadm settle --timeout=1 >/dev/null 2>&1 || sleep 1
		waited=$((waited + 1))
	done
	return 0
}

# --- 3. Менеджер пристроїв --------------------------------------------------
# Ядро надсилає події про знайдені шини через Netlink; udevd зіставляє
# ідентифікатори заліза й через modprobe тягне модулі саме тих контролерів
# (NVMe, SATA, SAS), які реально є в цій машині.
start_udev() {
	udevd_bin=""
	for cand in /lib/systemd/systemd-udevd /usr/lib/systemd/systemd-udevd \
		/sbin/udevd /bin/udevd; do
		[ -x "$cand" ] && { udevd_bin=$cand; break; }
	done
	[ -n "$udevd_bin" ] || panic "у initramfs немає udevd"

	"$udevd_bin" --daemon --resolve-names=never || panic "udevd не запустився"
	udevadm trigger --type=subsystems --action=add >/dev/null 2>&1
	udevadm trigger --type=devices --action=add >/dev/null 2>&1
	udevadm settle --timeout=30 >/dev/null 2>&1
}

stop_udev() {
	# Перед переходом udevd треба зупинити: його бінарник лежить у rootfs,
	# яку switch_root зараз зітре.
	udevadm control --exit >/dev/null 2>&1
}

# --- 4. Збирання блокової топології -----------------------------------------
open_luks() {
	uuid=$1
	node="/dev/disk/by-uuid/$uuid"
	name="luks-$uuid"

	[ -b "/dev/mapper/$name" ] && return 0
	wait_for_device "$node" || panic "не з'явився зашифрований том $uuid"

	# Спершу пробуємо ключ, запечатаний у TPM2: clevis тримає прив'язку
	# в самому заголовку LUKS, тож питати нічого не треба.
	if command -v clevis >/dev/null 2>&1 &&
		clevis luks unlock -d "$node" -n "$name" >/dev/null 2>&1; then
		log "том $uuid відкрито ключем із TPM2"
		return 0
	fi

	# TPM2 ключа не дав (інший стан PCR, немає прив'язки) — питаємо людину.
	tries=0
	while ! cryptsetup luksOpen "$node" "$name"; do
		tries=$((tries + 1))
		[ "$tries" -ge 3 ] && panic "пароль до тому $uuid не підійшов"
		log "спроба $tries з 3"
	done
}

assemble_storage() {
	if command -v mdadm >/dev/null 2>&1; then
		# --run піднімає масив і тоді, коли частина дисків іще не бачиться.
		mdadm --assemble --scan --run >/dev/null 2>&1 ||
			log "mdadm: масивів RAID не зібрано"
	fi

	for uuid in $luks_uuids; do
		open_luks "$uuid"
	done

	if command -v vgchange >/dev/null 2>&1; then
		# --sysinit не чіпає udev-правил і не чекає на демона lvmetad.
		vgchange --activate y --sysinit >/dev/null 2>&1 ||
			log "vgchange: логічних томів LVM немає"
	fi
}

# --- 5. Монтування справжнього кореня ---------------------------------------
mount_sysroot() {
	root_dev=$(resolve_spec "$root_spec")
	wait_for_device "$root_dev" || panic "кореневий пристрій $root_spec не з'явився"

	opts=$root_mode
	[ -n "$root_flags" ] && opts="$opts,$root_flags"

	# Корінь монтуємо тільки для читання: перевірку ФС і перемонтування
	# на запис зробить уже системний менеджер на справжньому корені.
	mount -t "$root_fstype" -o "$opts" "$root_dev" /sysroot ||
		panic "не монтується $root_dev у /sysroot"

	[ -x "/sysroot$user_init" ] ||
		panic "на новому корені немає запускного $user_init"
}

mount_pseudo
parse_cmdline
start_udev
assemble_storage
mount_sysroot
stop_udev

log "сховище зібране, передаю керування $user_init"
exec /sbin/switch_root /sysroot "$user_init"
panic "switch_root не спрацював"

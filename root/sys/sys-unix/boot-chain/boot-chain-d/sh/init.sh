#!/bin/sh
# /init усередині initramfs: перший процес простору користувача, PID 1.
#
# Його робота — від голого ядра з розпакованим cpio-архівом у пам'яті довести
# систему до стану, у якому справжній корінь змонтовано в /sysroot, і віддати
# номер 1 системному менеджеру через switch_root.
#
# Виходити звідси не можна: exit у PID 1 — це негайна паніка ядра.

set -u

PATH=/sbin:/bin:/usr/sbin:/usr/bin
export PATH

ROOT_SPEC=""       # значення root= як його дав завантажувач
ROOT_FSTYPE=""     # rootfstype=, якщо задано
ROOT_FLAGS=""      # rootflags=
MOUNT_MODE="ro"    # ro / rw
INIT_PATH="/sbin/init"
LUKS_UUIDS=""      # rd.luks.uuid=…
LVM_NEEDED=0
DEV_TIMEOUT=30     # секунд очікування появи пристрою
BREAK_AT=""        # rd.break=cmdline|premount|mount

log()  { echo "<6>initramfs: $*" > /dev/kmsg 2>/dev/null || echo "initramfs: $*"; }
warn() { echo "<4>initramfs: $*" > /dev/kmsg 2>/dev/null || echo "initramfs: $*" >&2; }

# Аварійна оболонка на консолі: єдиний спосіб подивитися, де саме стало.
emergency_shell() {
    warn "$1"
    warn "аварійна оболонка; exit — спроба продовжити"
    if [ -c /dev/console ]; then
        setsid sh -c 'exec sh -i < /dev/console > /dev/console 2>&1' || sh -i
    else
        sh -i
    fi
}

# Далі йти нікуди. Померти теж не можна — тому висимо, лишаючи консоль живою.
panic() {
    warn "ФАТАЛЬНО: $*"
    emergency_shell "система не завантажилася"
    warn "продовжити не вдалося; PID 1 лишається живим, перезавантажте машину"
    while : ; do
        sleep 3600
    done
}

maybe_break() {
    [ "$BREAK_AT" = "$1" ] || return 0
    emergency_shell "зупинка на точці rd.break=$1"
}

mount_pseudo_filesystems() {
    mkdir -p /proc /sys /dev /run
    mount -t proc     -o nosuid,noexec,nodev    proc     /proc || panic "немає /proc"
    mount -t sysfs    -o nosuid,noexec,nodev    sysfs    /sys  || panic "немає /sys"
    mount -t devtmpfs -o nosuid,mode=0755       devtmpfs /dev  || panic "немає /dev"
    mount -t tmpfs    -o nosuid,nodev,mode=0755 tmpfs    /run  || panic "немає /run"
    mkdir -p /dev/pts /run/cryptsetup
    mount -t devpts -o nosuid,noexec,gid=5,mode=0620 devpts /dev/pts \
        || warn "/dev/pts не змонтовано"
}

parse_cmdline() {
    for param in $(cat /proc/cmdline); do
        case "$param" in
            root=*)         ROOT_SPEC="${param#root=}" ;;
            rootfstype=*)   ROOT_FSTYPE="${param#rootfstype=}" ;;
            rootflags=*)    ROOT_FLAGS="${param#rootflags=}" ;;
            rootdelay=*)    DEV_TIMEOUT="${param#rootdelay=}" ;;
            ro)             MOUNT_MODE="ro" ;;
            rw)             MOUNT_MODE="rw" ;;
            init=*)         INIT_PATH="${param#init=}" ;;
            rd.luks.uuid=*) LUKS_UUIDS="$LUKS_UUIDS ${param#rd.luks.uuid=}" ;;
            rd.lvm.vg=*)    LVM_NEEDED=1 ;;
            rd.break=*)     BREAK_AT="${param#rd.break=}" ;;
            rd.break)       BREAK_AT="premount" ;;
        esac
    done
    [ -n "$ROOT_SPEC" ] || panic "у командному рядку ядра немає root="
}

# root=UUID=… та подібне — це не шлях, а запит до символічних посилань udev.
resolve_spec() {
    case "$1" in
        UUID=*)      echo "/dev/disk/by-uuid/${1#UUID=}" ;;
        PARTUUID=*)  echo "/dev/disk/by-partuuid/${1#PARTUUID=}" ;;
        LABEL=*)     echo "/dev/disk/by-label/${1#LABEL=}" ;;
        /dev/*)      echo "$1" ;;
        *)           echo "" ;;
    esac
}

start_udev() {
    if [ -x /lib/systemd/systemd-udevd ]; then
        /lib/systemd/systemd-udevd --daemon || panic "udevd не запустився"
    elif [ -x /sbin/udevd ]; then
        /sbin/udevd --daemon || panic "udevd не запустився"
    else
        warn "udevd відсутній: покладаємось на devtmpfs без стійких посилань"
        return 0
    fi
    # Ядро вже виявило залізо до нашого старту — просимо повторити події.
    udevadm trigger --action=add --type=subsystems
    udevadm trigger --action=add --type=devices
    udevadm settle --timeout="$DEV_TIMEOUT" || warn "черга udev не спорожніла вчасно"
}

wait_for_device() {
    device="$1"
    waited=0
    while [ ! -e "$device" ]; do
        if [ "$waited" -ge "$DEV_TIMEOUT" ]; then
            return 1
        fi
        sleep 1
        waited=$((waited + 1))
        udevadm settle --timeout=1 >/dev/null 2>&1
    done
    return 0
}

assemble_raid() {
    command -v mdadm >/dev/null 2>&1 || return 0
    [ -e /proc/mdstat ] || return 0
    # Суперблоки самі скажуть, з чого збирати масиви.
    mdadm --assemble --scan >/dev/null 2>&1
    if grep -q '^md' /proc/mdstat 2>/dev/null; then
        log "MD RAID зібрано"
    fi
}

unlock_luks() {
    [ -n "$LUKS_UUIDS" ] || return 0
    command -v cryptsetup >/dev/null 2>&1 || panic "cryptsetup відсутній в initramfs"

    for uuid in $LUKS_UUIDS; do
        source_dev="/dev/disk/by-uuid/$uuid"
        name="luks-$uuid"

        [ -e "/dev/mapper/$name" ] && continue
        wait_for_device "$source_dev" || panic "зашифрований том $uuid не з'явився"

        # Спершу пробуємо ключ із TPM2: за збігу PCR пароль не знадобиться.
        if [ -x /lib/systemd/systemd-cryptsetup ] \
           && cryptsetup luksDump "$source_dev" | grep -q 'systemd-tpm2'; then
            if /lib/systemd/systemd-cryptsetup attach "$name" "$source_dev" - \
                   tpm2-device=auto; then
                log "том $uuid відкрито ключем із TPM2"
                continue
            fi
            warn "TPM2 не віддав ключ — питаємо пароль"
        fi

        tries=0
        while [ "$tries" -lt 3 ]; do
            if cryptsetup luksOpen "$source_dev" "$name"; then
                break
            fi
            tries=$((tries + 1))
            warn "невірний пароль ($tries з 3)"
        done
        [ -e "/dev/mapper/$name" ] || panic "не вдалося розшифрувати $uuid"
        log "том $uuid відкрито"
    done
}

activate_lvm() {
    command -v vgchange >/dev/null 2>&1 || return 0
    if [ "$LVM_NEEDED" -eq 0 ]; then
        # Явної вказівки не було; якщо фізичних томів немає, вихід дешевий.
        vgscan --mknodes >/dev/null 2>&1 || return 0
    fi
    vgchange -ay >/dev/null 2>&1 || warn "активація груп томів LVM не вдалася"
    udevadm settle --timeout="$DEV_TIMEOUT" >/dev/null 2>&1
}

mount_root() {
    device=$(resolve_spec "$ROOT_SPEC")
    [ -n "$device" ] || panic "не розумію root=$ROOT_SPEC"

    wait_for_device "$device" \
        || panic "кореневий пристрій $device не з'явився за ${DEV_TIMEOUT}с"

    mkdir -p /sysroot
    options="$MOUNT_MODE"
    [ -n "$ROOT_FLAGS" ] && options="$options,$ROOT_FLAGS"

    if [ -n "$ROOT_FSTYPE" ]; then
        mount -t "$ROOT_FSTYPE" -o "$options" "$device" /sysroot \
            || panic "не змонтувати $device як $ROOT_FSTYPE"
    else
        mount -o "$options" "$device" /sysroot \
            || panic "не змонтувати $device (тип визначався автоматично)"
    fi
    log "корінь змонтовано з $device"
}

# /usr, винесений на окремий том, мусить бути на місці ще до переходу:
# після switch_root його вже нікому підняти — сам systemd лежить у /usr.
mount_usr() {
    fstab="/sysroot/etc/fstab"
    [ -r "$fstab" ] || return 0

    while read -r spec mountpoint fstype options rest; do
        case "$spec" in
            ''|\#*) continue ;;
        esac
        [ "$mountpoint" = "/usr" ] || continue

        device=$(resolve_spec "$spec")
        [ -n "$device" ] || device="$spec"
        wait_for_device "$device" || panic "том /usr ($device) не з'явився"

        mount -t "${fstype:-auto}" -o "ro,${options:-defaults}" "$device" /sysroot/usr \
            || panic "не змонтувати /usr з $device"
        log "/usr змонтовано з $device"
    done < "$fstab"
}

mount_pseudo_filesystems
parse_cmdline
maybe_break cmdline

start_udev
assemble_raid
unlock_luks
activate_lvm
maybe_break premount

mount_root
mount_usr
maybe_break mount

[ -x "/sysroot$INIT_PATH" ] || panic "у новому корені немає $INIT_PATH"

log "передаємо керування $INIT_PATH на справжньому корені"
# Не fork: той самий процес, той самий PID 1, інший образ у пам'яті.
exec switch_root /sysroot "$INIT_PATH"

panic "switch_root повернувся — образ не замінився"

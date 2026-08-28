#!/usr/bin/env bash
set -euo pipefail

TARGET_DIR="${1:-/mnt}"

cleanup() {
    echo -e "\n[!] Вихід із середовища. Виконується безпечне розмонтування..."
    for fs in dev/pts dev sys proc run; do
        if mountpoint -q "${TARGET_DIR}/${fs}"; then
            umount -l "${TARGET_DIR}/${fs}" || true
        fi
    done
    echo "[✓] Усі псевдо-ФС успішно відключено."
}

trap cleanup EXIT INT TERM

if [[ $EUID -ne 0 ]]; then
    echo "[-] Помилка: Скрипт вимагає прав суперкористувача (root)" >&2
    exit 1
fi

echo "[+] Підготовка псевдо-файлових систем у ${TARGET_DIR}..."
mkdir -p "${TARGET_DIR}"/{proc,sys,dev,run}

mount -t proc proc "${TARGET_DIR}/proc"
mount --rbind /sys "${TARGET_DIR}/sys" && mount --make-rslave "${TARGET_DIR}/sys"
mount --rbind /dev "${TARGET_DIR}/dev" && mount --make-rslave "${TARGET_DIR}/dev"
mount --rbind /run "${TARGET_DIR}/run" && mount --make-rslave "${TARGET_DIR}/run"

if [[ -f /etc/resolv.conf ]]; then
    cp -L /etc/resolv.conf "${TARGET_DIR}/etc/resolv.conf" 2>/dev/null || true
fi

echo "[+] Вхід у chroot середовище ${TARGET_DIR}..."
chroot "${TARGET_DIR}" /bin/bash --login

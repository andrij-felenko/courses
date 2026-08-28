#!/usr/bin/env bash
set -euo pipefail

NEW_KERNEL="/boot/vmlinuz-6.10.0-rc1"
NEW_INITRD="/boot/initrd.img-6.10.0-rc1"
CMDLINE="root=UUID=f47a-4281-b661 console=ttyS0,115200 quiet"

echo "Завантаження нового ядра $NEW_KERNEL у пам'ять..."
./kexec_runner "$NEW_KERNEL" "$NEW_INITRD" "$CMDLINE"

echo "Ядро підготовлено. Запуск гарячого перезавантаження без POST..."
sudo systemctl kexec

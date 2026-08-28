# 1. Перевірка доступності змінних UEFI
ls -la /sys/firmware/efi/efivars

# 2. Встановлення двійкових файлів завантажувача у розділ ESP та оновлення NVRAM
grub-install --target=x86_64-efi \
             --efi-directory=/boot/efi \
             --bootloader-id=GRUB \
             --recheck

# 3. Створення нового конфігураційного файлу меню завантаження
update-grub                              # для Debian / Ubuntu
grub-mkconfig -o /boot/grub/grub.cfg     # для RHEL / Arch Linux

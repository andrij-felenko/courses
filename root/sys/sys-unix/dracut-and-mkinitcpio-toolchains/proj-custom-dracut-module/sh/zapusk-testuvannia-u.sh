# Тест 1: Успішна перевірка (файл /key.bin створено у тимчасовому диску або вшито)
qemu-system-x86_64 \
  -kernel /boot/vmlinuz-linux \
  -initrd /boot/initramfs-linux.img \
  -append "console=ttyS0 keycheck.path=/key.bin rd.break=pre-mount" \
  -nographic

# Тест 2: Помилка перевірки (файл ключа відсутній) -> Перехід у emergency shell
qemu-system-x86_64 \
  -kernel /boot/vmlinuz-linux \
  -initrd /boot/initramfs-linux.img \
  -append "console=ttyS0 keycheck.path=/nonexistent.bin" \
  -nographic

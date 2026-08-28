#!/bin/sh
# uki.sh — зібрати єдиний образ ядра з чотирьох файлів.
set -eu

STUB=/usr/lib/systemd/boot/efi/linuxx64.efi.stub
LINUX=/boot/vmlinuz-linux
INITRD=/boot/initramfs-linux.img
OSREL=/usr/lib/os-release
OUT=uki.efi

# Рядок пишемо printf, а не echo: echo додасть у кінці перевід рядка,
# і той байт стане частиною командного рядка.
printf '%s' 'root=UUID=6f1c8b2a-… ro quiet' > cmdline

# 1. Крок вирівнювання з заголовка PE (objdump друкує його шістнадцятковим).
align=$(objdump -p "$STUB" | awk '$1 == "SectionAlignment" { print $2 }')
align=$((0x$align))

# 2. Кінець останньої секції заглушки: перше, що вже точно вільне.
#    Рядки секцій у «objdump -h» починаються з номера: Idx Name Size VMA …
set -- $(objdump -h "$STUB" |
         awk '$1 ~ /^[0-9]+$/ { size = $3; vma = $4 } END { print size, vma }')
next=$((0x$1 + 0x$2))

# 3. Розкладка. Функція мусить МІНЯТИ next, тому вона не друкує адресу,
#    а присвоює її змінній: виклик через $(…) пішов би в підоболонку
#    і посунутий next загубився б разом з нею.
place() {                       # place <ім'я-змінної> <файл>
  next=$(( (next + align - 1) / align * align ))
  eval "$1=\$next"
  next=$(( next + $(stat -Lc%s "$2") ))
}

place osrel_at   "$OSREL"
place cmdline_at cmdline
place linux_at   "$LINUX"
place initrd_at  "$INITRD"

# 4. Власне склеювання. Порядок аргументів = порядок записів у таблиці
#    секцій, тому подаємо їх у тому ж порядку, у якому зростають адреси.
objcopy \
  --add-section .osrel="$OSREL"   --change-section-vma .osrel=$osrel_at     \
  --add-section .cmdline=cmdline  --change-section-vma .cmdline=$cmdline_at \
  --add-section .linux="$LINUX"   --change-section-vma .linux=$linux_at     \
  --add-section .initrd="$INITRD" --change-section-vma .initrd=$initrd_at   \
  "$STUB" "$OUT"

printf 'osrel %#x  cmdline %#x  linux %#x  initrd %#x\n' \
       "$osrel_at" "$cmdline_at" "$linux_at" "$initrd_at"

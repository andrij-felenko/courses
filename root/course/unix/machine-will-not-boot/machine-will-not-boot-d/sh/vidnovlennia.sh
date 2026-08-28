# 1. Виявлення фізичних накопичувачів
lsblk -f

# 2. Збирання програмного RAID (якщо використовується mdadm)
mdadm --assemble --scan

# 3. Відкриття зашифрованих томів LUKS
cryptsetup luksOpen /dev/nvme0n1p3 cryptroot

# 4. Активація логічних томів LVM
vgscan
vgchange -ay

# 5. Перевірка цілісності кореневої ФС перед монтуванням
e2fsck -f /dev/mapper/vg0-root

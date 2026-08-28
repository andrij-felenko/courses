# 1. Перевірка очікуваного ядром UUID
cat /proc/cmdline

# 2. Перегляд реальних UUID виявлених дисків
blkid

# 3. Перевірка наявності блокових пристроїв у ядрі
cat /proc/partitions

# 4. Якщо диск зашифрований LUKS — ручне відкриття контейнера
cryptsetup luksOpen /dev/nvme0n1p3 cryptroot

# 5. Якщо використовується LVM — сканування та активація томів
lvm vgscan
lvm vgchange -ay

# ── формат: що вросло під час mkfs ──────────────────────────────────────────
dumpe2fs -h /dev/nvme0n1p2     # суперблок ext4 без дампу груп
tune2fs -l /dev/nvme0n1p2      # те саме, іншим виглядом
xfs_info /mnt/data             # геометрія XFS: bsize, agcount, crc, reflink, log
btrfs filesystem show          # склад тому Btrfs
btrfs filesystem usage /mnt    # профілі й правдиве вільне місце
dump.f2fs -d 1 /dev/mmcblk0p2  # суперблок F2FS
cat /sys/fs/f2fs/mmcblk0p1/features   # перелік можливостей змонтованої F2FS
lsblk -f                       # тип ФС, мітка, UUID по всіх пристроях

# ── прохання: що написано в конфігурації ────────────────────────────────────
cat /etc/fstab
systemctl cat 'srv-pool.mount' 2>/dev/null

# ── дійсність: що ядро підставило зараз ─────────────────────────────────────
cat /proc/mounts               # чинні параметри, з типовими значеннями ядра
findmnt -o TARGET,SOURCE,FSTYPE,OPTIONS
cat /proc/self/mountinfo       # плюс корінь піддерева й правила поширення

# Монтування procfs
mount -t proc proc /mnt/proc

# Рекурсивне зв'язування sysfs, devtmpfs та run
mount --rbind /sys /mnt/sys
mount --make-rslave /mnt/sys

mount --rbind /dev /mnt/dev
mount --make-rslave /mnt/dev

mount --rbind /run /mnt/run
mount --make-rslave /mnt/run

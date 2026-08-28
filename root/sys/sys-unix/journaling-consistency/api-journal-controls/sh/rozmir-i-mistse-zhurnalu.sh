# 1. окремий швидкий пристрій цілком стає журналом
mke2fs -O journal_dev -b 4096 /dev/nvme0n1p3

# 2а. нова ФС одразу з ним
mke2fs -t ext4 -b 4096 -J device=/dev/nvme0n1p3 /dev/sda1

# 2б. або приєднати до наявної (журналу в ній бути не повинно)
tune2fs -J device=/dev/nvme0n1p3 /dev/sda1

# 3. якщо номер пристрою змінився після перезавантаження
mount -o journal_path=/dev/nvme0n1p3 /dev/sda1 /mnt

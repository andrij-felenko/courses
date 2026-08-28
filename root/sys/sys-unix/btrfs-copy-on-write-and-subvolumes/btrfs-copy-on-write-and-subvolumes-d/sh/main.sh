# 1. Створення базового Read-Only знімка
btrfs subvolume snapshot -r /home /backup/home_base

# 2. Передача базового знімка на зовнішній накопичувач або по мережі
btrfs send /backup/home_base | btrfs receive /mnt/remote_backup/

# 3. Через добу: створення нового знімка
btrfs subvolume snapshot -r /home /backup/home_2026_08_12

# 4. Інкрементальна передача ЛИШЕ РІЗНИЦІ між home_base та home_2026_08_12
btrfs send -p /backup/home_base /backup/home_2026_08_12 | btrfs receive /mnt/remote_backup/

# 1. Переведення фізичного пристрою в режим Read-Only на рівні блокового шару
blockdev --setro /dev/sdb1

# 2. Отримання точного розміру пристрою в секторах (по 512 байтів)
SIZE=$(blockdev --getsz /dev/sdb1)

# 3. Створення тимчасового файлу для збереження змін (наприклад, у tmpfs RAM-диску)
truncate -s 10G /tmp/overlay.img
LOOP_DEV=$(losetup --find --show /tmp/overlay.img)

# 4. Створення віртуального блокового пристрою COW через dmsetup
# Синтаксис таблиці: 0 <сектори> snapshot <базовий_пристрій> <cow_пристрій> <персистентність> <chunk_size>
echo "0 $SIZE snapshot /dev/sdb1 $LOOP_DEV P 8" | dmsetup create repair-snap

# 5. Тепер /dev/mapper/repair-snap є повною копією диска, відкритою для запису!
# Виконуємо відновлення на віртуальному пристрої:
e2fsck -f -y /dev/mapper/repair-snap

# 6. Перевіряємо результат: чи монтується відновлений образ
mount /dev/mapper/repair-snap /mnt/test

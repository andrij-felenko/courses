# Генерація 512-бітного випадкового ключа (64 байти в hex)
KEY=$(dd if=/dev/urandom bs=64 count=1 status=none | xxd -p -c 64)

# Отримання розміру блокового пристрою в секторах по 512 байтів
SECTORS=$(blockdev --getsz /dev/loop0)

# Створення віртуального відображення dm-crypt
dmsetup create secure_disk --table "0 $SECTORS crypt aes-xts-plain64 $KEY 0 /dev/loop0 0 1 sector_size:4096"

# Перевірка стану та параметрів створеної цілі
dmsetup status secure_disk
dmsetup table --showkeys secure_disk

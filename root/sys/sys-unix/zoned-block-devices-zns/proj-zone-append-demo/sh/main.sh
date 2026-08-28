# Форматуємо пристрій під zonefs
$ sudo mkfs.zonefs /dev/nullb0

# Створюємо точку монтування та монтуємо ФС
$ sudo mkdir -p /mnt/zonefs
$ sudo mount -t zonefs /dev/nullb0 /mnt/zonefs

# Перевіряємо структуру файлів
$ ls -la /mnt/zonefs/seq/ | head -n 5
-rw-r--r-- 1 root root 0 Aug 12 12:00 0
-rw-r--r-- 1 root root 0 Aug 12 12:00 1
-rw-r--r-- 1 root root 0 Aug 12 12:00 2

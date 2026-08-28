# Перегляд списку зареєстрованих VFS-типів ядра
cat /proc/filesystems

# Виявлення процесів, що блокують точку монтування
fuser -vm /mnt/point
lsof +f -- /mnt/point

# Перевірка холдерів (холдер утримує пристрій через bd_open_exclusive)
# Якщо каталог містить записи, пристрій зайнятий LVM, dm-crypt або md-масивом:
ls -l /sys/class/block/<dev_name>/holders/

# Перевірка підлеглих пристроїв (slaves):
ls -l /sys/class/block/<dev_name>/slaves/

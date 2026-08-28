# 1. Створюємо тимчасову точку доступу
# mkdir /mnt/inspect_root

# 2. Виконуємо bind mount кореневої файлової системи
# mount --bind / /mnt/inspect_root

# 3. Скануємо вміст каталогу БЕЗ накладених монтувань
# du -sh /mnt/inspect_root/mnt/storage
60G    /mnt/inspect_root/mnt/storage

# 4. Видаляємо прихований файл
# rm /mnt/inspect_root/mnt/storage/backup.tar

# 5. Прибираємо тимчасове монтування
# umount /mnt/inspect_root
# rmdir /mnt/inspect_root

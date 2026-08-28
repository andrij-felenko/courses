# Створюємо дзеркальний масив RAID1
sudo mdadm --create /dev/md0 --level=1 --raid-devices=2 \
    --metadata=1.2 /dev/loop0 /dev/loop1

# Створюємо файлову систему ext4 на новому масиві
sudo mkfs.ext4 -F /dev/md0

# Монтуємо масив у тестову точку монтування
sudo mkdir -p /mnt/raid-test
sudo mount /dev/md0 /mnt/raid-test

# Записуємо 400 Мегабайтів випадкових бінарних даних
sudo dd if=/dev/urandom of=/mnt/raid-test/testdata.bin bs=1M count=400 status=progress
sync

# Фіксуємо еталонну контрольну суму файлу
sha256sum /mnt/raid-test/testdata.bin | tee /tmp/raid-lab/checksum.orig

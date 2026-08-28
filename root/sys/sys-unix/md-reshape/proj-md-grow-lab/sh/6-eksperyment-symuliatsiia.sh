# Зупиняємо попередній масив та розмонтовуємо файлову систему
sudo umount /mnt/raid-test
sudo mdadm --stop /dev/md0

# Створюємо масив RAID5 на метаданих 1.0 з двох дисків
sudo mdadm --create /dev/md1 --level=5 --raid-devices=2 \
    --metadata=1.0 /dev/loop0 /dev/loop1

# Додаємо третій диск
sudo mdadm --add /dev/md1 /dev/loop2

# Запускаємо розширення з обов'язковим вказуванням резервного файлу у фоновому режимі
sudo mdadm --grow /dev/md1 --raid-devices=3 --backup-file=/tmp/raid-lab/reshape.bak &

# Миттєво перериваємо процес (імітуємо раптове вимикання живлення)
sleep 0.1
sudo killall -9 mdadm
sudo mdadm --stop /dev/md1 || sudo mdadm --manage /dev/md1 --stop

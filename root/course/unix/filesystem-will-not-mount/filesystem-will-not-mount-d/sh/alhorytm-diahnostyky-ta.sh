# 1. Перегляд повідомлень системного журналу для локалізації збійного юніта
journalctl -xb | grep -iE "mount|failed|timed out"

# 2. Перегляд списку юнітів, що завершилися з помилкою
systemctl --failed

# 3. Визначення реальних UUID наявних блокових пристроїв
blkid

# 4. Перевірка синтаксису /etc/fstab та відповідності UUID
cat /etc/fstab

# 5. Тестовий запуск генератора systemd у тимчасовий каталог
/lib/systemd/system-generators/systemd-fstab-generator /tmp/test-generator/

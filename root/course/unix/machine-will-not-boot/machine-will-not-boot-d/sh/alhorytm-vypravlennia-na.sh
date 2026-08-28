# 1. Локалізація причини збою в системному журналі
journalctl -xb | grep -iE "mount|failed|timed out"

# 2. Визначення збійного юніта
systemctl --failed

# 3. Переведення кореневого розділу в режим читання-запису (Read-Write)
mount -o remount,rw /

# 4. Редагування файлу /etc/fstab
# Необхідно або виправити помилковий UUID, або додати опцію nofail:
# UUID=xxxx-xxxx /data ext4 defaults,nofail,x-systemd.device-timeout=5s 0 2

# 5. Перезавантаження конфігурації генераторів systemd
systemctl daemon-reload

# 6. Продовження нормального завантаження без перезавантаження ОС
systemctl default

# 1. Збірка модуля у поточному каталозі
make

# 2. Завантаження модуля у ядро
sudo insmod demo_kobj.ko

# 3. Перевірка наявності створеного каталогу та файлів атрибутів у sysfs
ls -la /sys/kernel/demo_kobj/

# 4. Читання атрибута status (кожен новий виклик інкрементує лічильник)
cat /sys/kernel/demo_kobj/status
# Вивід: 42
cat /sys/kernel/demo_kobj/status
# Вивід: 43

# 5. Перевірка читання та запису нового стану в control
cat /sys/kernel/demo_kobj/control
# Вивід: default_state

echo "active_mode" | sudo tee /sys/kernel/demo_kobj/control
cat /sys/kernel/demo_kobj/control
# Вивід: active_mode

# 6. Перевірка ядерних повідомлень через dmesg
dmesg | tail -n 5

# 7. Вивантаження модуля та перевірка видалення каталогу з sysfs
sudo rmmod demo_kobj

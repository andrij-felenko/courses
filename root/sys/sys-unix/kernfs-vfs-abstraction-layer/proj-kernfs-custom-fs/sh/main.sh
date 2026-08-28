# Перегляд структури каталогів
ls -la /mnt/demo_fs
ls -la /mnt/demo_fs/control

# Читання статичного текстового атрибута
cat /mnt/demo_fs/info

# Читання поточного значення лічильника
cat /mnt/demo_fs/control/status

# Модифікація значення лічильника через echo
echo "420" | sudo tee /mnt/demo_fs/control/status

# Перевірка оновленого стану
cat /mnt/demo_fs/control/status

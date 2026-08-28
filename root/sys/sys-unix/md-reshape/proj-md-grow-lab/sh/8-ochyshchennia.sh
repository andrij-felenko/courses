# Зупиняємо тестовий масив
sudo mdadm --stop /dev/md1 2>/dev/null || true

# Звільняємо петльові пристрої loop
for i in {0..4}; do
    sudo losetup -d /dev/loop${i} 2>/dev/null || true
done

# Видаляємо робочий каталог із файлами-образами
rm -rf /tmp/raid-lab

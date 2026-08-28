# Створюємо робочий каталог експерименту
mkdir -p /tmp/raid-lab && cd /tmp/raid-lab

# Створюємо 5 файлів-образів розміром по 1 ГіБ кожен
for i in {0..4}; do
    truncate -s 1G disk${i}.img
done

# Прив'язуємо образи до віртуальних петльових пристроїв loop
for i in {0..4}; do
    sudo losetup -fP disk${i}.img
done

# Перевіряємо призначені ядром імена блокових пристроїв
losetup -a | grep raid-lab

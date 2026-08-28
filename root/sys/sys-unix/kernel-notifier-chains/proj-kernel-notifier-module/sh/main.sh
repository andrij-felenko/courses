# 1. Компільовано модуль ядра
make

# 2. Завантажуємо зібраний бінарний файл .ko у ядро
sudo insmod my_netdev_notifier.ko

# 3. Створюємо новий віртуальний мережевий адаптер test_dummy0
sudo ip link add name test_dummy0 type dummy

# 4. Змінюємо розмір MTU інтерфейсу
sudo ip link set test_dummy0 mtu 1400

# 5. Піднімаємо інтерфейс (генерує NETDEV_UP)
sudo ip link set test_dummy0 up

# 6. Опускаємо інтерфейс (генерує NETDEV_GOING_DOWN та NETDEV_DOWN)
sudo ip link set test_dummy0 down

# 7. Видаляємо віртуальний інтерфейс із системи
sudo ip link delete test_dummy0

# 8. Вивантажуємо модуль сповіщень
sudo rmmod my_netdev_notifier

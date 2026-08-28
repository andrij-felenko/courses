# Збірка модуля
make

# Завантаження модуля у ядро
sudo insmod kallsyms_probe_module.ko

# Перегляд результатів виводу у системному журналі
sudo dmesg | tail -n 10

# Вивантаження модуля
sudo rmmod kallsyms_probe_module

# 1. Скомпілювати модуль ядра
$ make

# 2. Завантажити модуль у ядро
$ sudo insmod demo_debug_module.ko

# 3. Перевірити вивід системного логу dmesg
$ dmesg | tail -n 5

# 4. Прочитати звіт із debugfs
$ sudo cat /sys/kernel/debug/demo_driver/status_report

# 5. Змінити значення лічильника та прапорця налагодження
$ echo 42 | sudo tee /sys/kernel/debug/demo_driver/packet_count
$ echo Y | sudo tee /sys/kernel/debug/demo_driver/debug_enabled

# 6. Перевірити оновлений звіт
$ sudo cat /sys/kernel/debug/demo_driver/status_report

# 7. Вивантажити модуль з ядра
$ sudo rmmod demo_debug_module

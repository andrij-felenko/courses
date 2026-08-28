# 1. Компіляція модуля ядра
make

# 2. Перевірка наявності debugfs та монтування за потреби
sudo mount -t debugfs none /sys/kernel/debug

# 3. Завантаження модуля в ядро
sudo insmod kasan_demo.ko

# 4. Виклик сценарію Use-After-Free
echo 1 | sudo tee /sys/kernel/debug/kasan_demo/trigger_uaf

# 5. Виклик сценарію Out-of-Bounds Write
echo 1 | sudo tee /sys/kernel/debug/kasan_demo/trigger_oob_write

# 6. Виклик сценарію Out-of-Bounds Read
echo 1 | sudo tee /sys/kernel/debug/kasan_demo/trigger_oob_read

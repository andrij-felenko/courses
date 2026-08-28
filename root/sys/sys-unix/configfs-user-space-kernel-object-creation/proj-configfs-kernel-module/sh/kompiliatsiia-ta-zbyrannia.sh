# 1. Збирання модуля
make

# 2. Монтування configfs, якщо вона не була змонтована автоматично
sudo mount -t configfs none /sys/kernel/config

# 3. Завантаження модуля ядра
sudo insmod demo_configfs.ko

# 4. Перевірка наявності кореневого каталогу підсистеми
ls -la /sys/kernel/config/demo_target/
